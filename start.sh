#!/bin/bash
# run this script as root or with sudo
# it will start a screen session, which you can connect to with:
# sudo screen -r mpf

if [ -z "$STY" ]; then exec screen -dm -S mpf /bin/bash "$0"; fi

GAME="/home/sysop/Fan-Tas-Tic-machine"

while true
do
	# mpf needs to start as root to access the LED DMD
	/home/sysop/.pyenv/shims/mpf both $GAME -Pt
	echo "MPF EXIT :(  restarting in 5 s ..."
	sleep 5
done
