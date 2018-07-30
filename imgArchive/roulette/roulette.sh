#!/bin/bash
convert roulette.svg -duplicate 125 -distort SRT %[fx:t*t/30] \
    -set delay 2 -loop 0 -reverse -resize 32x32 +map roulette.gif
