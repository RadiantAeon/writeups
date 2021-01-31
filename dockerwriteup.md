# Docker Writeup
Basically, you get a shell in a docker container. You're supposed to find information and feed it to an oracle.
The required info is:
- the cpu model
- the container id
- a secret that the oracle writes in after running
- the container id of **different** container id
- the container id of the oracle service

The steps are as follows to get the info:
- `lscpu` gives you the cpu model
- googlefu tells you that the container id is in `/proc/self/cgroup`
The long string after `/docker` in `/proc/self/cgroup` is the container id
- You have to read the secret without closing the program as it generates a new secret every run.
Open the program in the background by running the connection command (`socat - UNIX-CONNECT:/oracle.sock`) with ` &` on the end
This means we can still see the output but our input does not get piped into it.
Move the program to the foreground using `fg` which allows us to interact with it again.
Enter the cpu model and container id to make it write the secret.
Then, we enter `ctrl+z` and then `bg`. We have to use a solve script because of this. If you try entering `ctrl+z` without a solve script, `nc` will disconnect you.
Then just simply do `cat /secret`. Do not reattach yet.
- Get another container id
`/proc/self/cgroup` doesn't contain the id of a different container. Neither do any of the other `cgroup` files in `/proc`. I just assumed that a `cgroup` file that applied to the whole system including the host would include all the other container ids. Just run `find . "cgroup"` and a lot of cgroup files/directories will pop up. I used the one in `/sys/kernel/slab/:A-0000208/cgroup` which actually contains a bunch of files that happen to have container ids in their file names. Choose one that isn't our container id and use that as the other one.
- Get the oracle container id
I just guessed this one. Assume that the oldest one is the oracle container, and it works. In context of the previous step, just get the first container id you see.

Reattach and enter the secret, other container id, and oracle container id, and it gives you the flag!