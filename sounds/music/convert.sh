#!/bin/bash
# convert sound files to .wav for better runtime performance
for fSource in *.ogg; do
  fDest="${fSource%.*}.wav"
  echo "$fSource --> $fDest"
  sox "$fSource" "$fDest"
done
echo "If all .wav files have been generated, delete the *.ogg files"
