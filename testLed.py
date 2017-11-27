#!/usr/bin/python3
"""
turn on a specific led
usage:
testLed.py /dev/ttyACM0 3200000 0 42
to turn on led 42 on channel 0.
set communication speed to 3200000 (high speed mode)
try 1700000 or 3200000 here
turns off all other leds on that channel
"""
import serial, sys
from sys import argv

def updateLed( sObj, dat=None, channel=0 ):
    if dat is None:
        nLeds = 1024
        ledDat = bytearray( os.urandom( nLeds*3 ) )
    elif type(dat) is int:
        nLeds = dat
        ledDat = bytearray( os.urandom( nLeds*3 ) )
    else:
        nLeds = len(dat)
        ledDat = bytearray( dat )
    sDat = bytes("LED {0} {1}\n".format(channel, len(ledDat)), "utf8") + ledDat
    sObj.write( sDat )
    
if len(argv) != 5:
    print(__doc__)
    sys.exit()
    
aTTY     = argv[1]
aSPEED   = argv[2]
aCHANNEL = argv[3]
aLED     = int( argv[4], 0 )
    
with serial.Serial( aTTY, timeout=1 ) as s:
    s.read_all()          #Clear receive buffer
    s.write(b"\n*IDN?\n") #First \n clears send buffer
    print( s.read_until() )
    configStr = "LEC {} {}\n".format(aSPEED, aCHANNEL)
#    print( configStr )
    s.write( bytearray(configStr,"ascii") )
    z = bytearray(1024*3)
    z[ aLED*3:aLED*3+3 ] = [255]*3
    updateLed(s, z, aCHANNEL )
