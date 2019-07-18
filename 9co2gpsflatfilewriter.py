#!/usr/bin/python3

import serial, time, socket,  io, struct, string, sys
import numpy as np
import atexit

# Modifying filename for to start with machine name wayback
# hostname = os.uname()[1]  # data type is str
# This is the same as the 4... program. 
#Modifying program to write both sensor fields the same work with four sensors
# by commenting out all calls to USB2 and USB3
#
# Plug the USB CO2 sensor in first, GPS second
ttyusb0 = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3.0)
trialread0 = ttyusb0.readline()

ttyusb1 = serial.Serial("/dev/ttyUSB1", baudrate=9600, timeout=3.0)
trialread1 = ttyusb1.readline()
#ttyusb2 = serial.Serial("/dev/ttyUSB2", baudrate=9600, timeout=3.0)
#trialread2= ttyusb2.readline()

#ttyusb3 = serial.Serial("/dev/ttyUSB3", baudrate=9600, timeout=3.0)
#trialread3 = ttyusb3.readline()

#print("Trial read0 ",trialread0,"Short string ",trialread0[0:1])
looptest = 20
#Determine which of the two USB data lines is the CO2 sensor.
#Then assign the cozirinput data read handle to the correct USB port

print("Trialread0 ",trialread0," Trialread1 ",trialread1)
print("Trialread0 substring ",trialread0[0:3]," Trialread1 substring ",trialread1[0:3])

gpsinput=ttyusb0    # Global one of these assignments is wrong
cozirinput=ttyusb0  # Global

#----------------begin block to determine USB and sensor match---------

#Work on trialread0 first. Read until the value matches either CO2 or GPS data
trialread0 = ttyusb0.readline()
while trialread0[0:3] != b' H ' or trialread0[0:6] != b'$GPGGA':
    trialread0 = ttyusb0.readline()
    if trialread0[0:3] == b' H ':   # usb0 is CO2 data
        cozirinput=ttyusb0
        print("USB0 has CO2 data line 42 ", trialread0)
        break

    if trialread0[0:6] == b'$GPGGA': # usb0 is GPS data
        gpsinput=ttyusb0
        print("USB0 has GPS data ", trialread0)
        break
    
#print("Work on trialread0 is done")

#Work on trialread1. Read until the value matches either CO2 or GPS data

#print("Work on trialread1 begins")
trialread1 = ttyusb1.readline()
print("Trialread1 ", trialread1)
while trialread1[0:3] != b' H ' or trialread1[0:6] != b'$GPGGA':
    trialread1 = ttyusb1.readline()
    #print("Trialread inside loop ", trialread1)
    if trialread1[0:3] == b' H ':   # usb1 is CO2 data
        cozirinput=ttyusb1
        print("USB1 has CO2 data ", trialread1)
        break

    if trialread1[0:6] == b'$GPGGA': # usb1 is GPS data
        gpsinput=ttyusb1
        print("USB1 has GPS data ", trialread1)
        break
    
#print("Work on trialread1 seems over")
    

# Following is a test of the above finding sensors code
# cozirinput=b"value not present"  # Global
# print("exited finding sensors first loop")
#while cozirinput == b'value not present':
#print("Cozirinput not OK ",cozirinput)
#co2data=cozirinput.readline()
#print("co2 data ", co2data)

while trialread0[0:6] == b'$GPGGA' :
    gpsinput=ttyusb0
    #print("USB0 has GPS data 81")
    #print("Trialread0 substring ",trialread0[0:6]," Trialread1 substring ",trialread1[0:6])
    break

while trialread1[0:6] == b'$GPGGA' :
    gpsinput=ttyusb1
    #print("USB1 has GPS data 87")
    break

filenametime = int(time.time())  # Making this a global variable. It becomes the integer timestamp of first data read.

def close_files_atexit():
    ttyusb0.close()
    ttyusb1.close()
#    ttyusb2.close()
#    ttyusb3.close()


def read_sensors():
    # Delay reading data until the 10th second of the UTC.
    # Makes the timestamp an integer 
    # Makes the next readcycle int value time
    #print("hello there 3")
    
    #readcycle= int(2) # alternate faster read
    readcycle= int(60) # Read cycle is an integer number of seconds
    inttime=int(time.time()) # inttime is an integer value of the unixtime
    # waittime is a future time readcycle + inttime reduced by time already elapsed.
    waittime= int(readcycle - (inttime % readcycle) + inttime) 
    #print(" waittime ", waittime, "Inttime ",inttime)
    while inttime < waittime :
        #print(" inttime ",inttime," waittime ",waittime)
        time.sleep(1)
        inttime=int(time.time())

    co2data = cozirinput.readline()
    #print("Co2 data ", co2data)
    #print("Co2data ",co2data, " byte 0 to 3 substring ",co2data[0:3])
    while co2data[0:3] != b' H ' :
        co2data=cozirinput.readline()
        print("Looping until first character of co2 sensor data is  H ")

    gpsdata=gpsinput.readline()
    #print("Gpsdata ",gpsdata, " byte 0 to 6 substring ",gpsdata[0:6])
    #GPS data has several report formats. Repeat until the GPGGA format is read
    while gpsdata[0:6] != b'$GPGGA' :
        gpsdata=gpsinput.readline()
        #print("Loop until GPGGA ",gpsdata)

    line_of_data = str(waittime) + str(" ") + str(co2data) + str(" ") + str(gpsdata) 
    #line_of_data = line_of_data + str(" ") + str(co2data2) + str(" ") + str(gpsdata1) 
    line_of_data=line_of_data.replace(',',' ') # Replace also done later, redundant
    print("Timestamped  ", line_of_data)
    #print("hello there 2")
    return line_of_data

def make_header():
    # Put information about the data being collected in "#" fields
    # at the top of the data file.
    # By type testing, hostname and programname are str type

    hostname=socket.gethostname()
    programname=sys.argv[0]
    commentname='co2 and gps data blank delimited'
    try  :
        commentname = sys.argv[1]
    except : commentname='co2 and gps'
    hashmark='# '
    space=' '
    endofline='\n'
    header=hashmark +hostname +space +programname +space +commentname +endofline
    #while 1:
    #    pass
    #print("Hello there 8")
    return header

# Write data to a file
def writelinesofco2andgpsdatatoafile():
    utctime = int(time.time())
    hostname=socket.gethostname()
    utcfilename=hostname+str(filenametime)+"_"+"co2gps52619"
    f1 = open(utcfilename,"a", buffering=1, encoding=None, )
    f1.write(make_header())
    loopnumber = 4322      # 1 times per min 60 min per hr 24 hr per day 3 days plus 2
    while loopnumber > 2 :
        s=str(read_sensors())
        s= s + "\n"
        #print("String before cleanup ",s)
        s=s.replace(',',' ')
        #print("String after cleanup- ",s)
        f1.write(s)
        loopnumber = loopnumber -1
        #print("Hello there 7")

# Begin main program
atexit.register(close_files_atexit)
#print("Hello there 6")
writelinesofco2andgpsdatatoafile()
read_sensors()

