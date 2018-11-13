#!/bin/bash
for fSource in *.ogg; do
  fDest="../sounds/music/${fSource%.*}.wav"
  echo "$fSource --> $fDest"
  sox "$fSource" "$fDest"
done
