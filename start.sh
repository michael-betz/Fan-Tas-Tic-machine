#!/bin/sh
if [ -z "$STY" ]; then exec screen -dm -S mpf /bin/bash "$0"; fi
GAME="/home/sysop/Fan-Tas-Tic-machine"
mpf $GAME -t &
sleep 5
sudo -u sysop mpf mc $GAME -t
