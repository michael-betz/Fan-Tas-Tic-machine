#!/bin/bash
for fSource in *.ogg; do
  fDest="./wav2/${fSource%.*}.wav"
  echo "$fSource --> $fDest"
  sox "$fSource" "$fDest"
done
