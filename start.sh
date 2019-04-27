#!/bin/sh
if [ -z "$STY" ]; then exec screen -dm -S mpf /bin/bash "$0"; fi
GAME="/home/sysop/Fan-Tas-Tic-machine"
# mpf will start as root and drop privilege
mpf $GAME -At &
sleep 5
# mpf mc will start as sysop
sudo -u sysop mpf mc $GAME -At
