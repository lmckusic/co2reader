#!/bin/bash
cd co2
# Script to start the current CO2 meter program 
# Small change to see how github takes it.
echo "Now in co2 python instrument subdirectory"
stty -F /dev/ttyUSB0 speed 9600 cs7
stty -F /dev/ttyUSB1 speed 9600 cs7

./9co2gpsflatfilewriter.py


