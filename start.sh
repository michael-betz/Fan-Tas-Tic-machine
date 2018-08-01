#!/bin/bash
screen -X -S mpf_daemon quit
echo "Starting Fan-Tas-Tic screen session"
screen -LdmS mpf_daemon bash -c "sleep 10; mpf both /home/sysop/Fan-Tas-Tic-machine/ -t"
