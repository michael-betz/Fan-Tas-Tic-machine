#!/usr/bin/python3
import os
for f in sorted(os.listdir(".")):
	print("-", f.split(".")[0] )
