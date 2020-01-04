#!/usr/bin/python3

import serial
import time
import socket  
import io
import struct 
import string
import sys
import atexit
import re
import numpy as np
"""
# Block of example data and code used for matching

# Sample good cozir sensor line note leading blank
# H 00563 T 01260 Z 00445 z 00445
#cozirdata=' H 00563 T 01260 Z 00445 z 00445'
lencozir=len(' H 00563 T 01260 Z 00445 z 00445')
lencozir
#lencozir=len(cozirdata)
lencozir
fourcozir=' H 00563 T 01260 Z 00445 z 00445'[0:5]
fourcozir
#fourcozir=cozirdata[0:5]
fourcozir
zvalcozir=' H 00563 T 01260 Z 00445 z 00445'[17:24]
zvalcozir
#zvalcozir=cozirdata[17:24]
zvalcozir
cozirtest=' H \d{5} T \d{5} Z \d{5}'
#cozirdata=' H 00563 T 01260 Z 00445 z 00445'
#re.match(cozirtest, cozirdata)
#matchcoz=re.match(cozirtest, cozirdata)
#matchcoz     # match object
#matchcoz[0]  # The matched data string
#matchcoz[0][17:24]  # The Z 00445 value string
# sreE_Match object; span=(0, 24), match=' H 00563 T 01260 Z 00445'>
# test for match with if match:
#print('cozir data length ',lencozir,' fourcozircharacters ', fourcozir, 'zval ',zvalcozir)

# Sample good gpgga data line

#$GPGGA,231148.000,3730.5294,N,12228.3616,W,1,03,2.29,177.3,M,-25.9,M,,*5C
lengpgga=len('$GPGGA,231148.000,3730.5294,N,12228.3616,W,1,03,2.29,177.3,M,-25.9,M,,*5C')
lengpgga
fivegpgga='$GPGGA,231148.000,3730.5294,N,12228.3616,W,1,03,2.29,177.3,M,-25.9,M,,*5C'[0:5]
fivegpgga
fixgpgga='$GPGGA,231148.000,3730.5294,N,12228.3616,W,1,03,2.29,177.3,M,-25.9,M,,*5C'[42:45]
fixgpgga
# work out tests for gps data using successful co2meter test
#print('gpgga data length ',lengpgga,' fivegpggachar ', fivegpgga, 'fixgpgga ',fixgpgga)
gpsdata='$GPGGA,231148.000,3730.5294,N,12228.3616,W,1,03,2.29,177.3,M,-25.9,M,,*5C'
gpsdata
#gpstest1='$GPGGA,231148.000,3730.5294,N,12228.3616,W,1'
gpstest='\$GPGGA,\d{6}.\d{3},\d{4}.\d{4},N,\d{5}.\d{4},W,1'
# gpstestfix2 looks for fix quality =2 for GPS on but no fix yet
gpstestfix2='\$GPGGA,\d{6}.\d{3},\d{4}.\d{4},N,\d{5}.\d{4},W,2'
# gpstestgpgga looks for starting characters only
gpstestgpgga='\$GPGGA'
gpstest
re.match(gpstest,gpsdata)
re.match(gpstest,gpsdata)[0]
matchgps=re.match(gpstest,gpsdata)[0]
matchgps
#'$GPGGA,231148.000,3730.5294,N,12228.3616,W,1'
matchgps[43:44]       # Fix quality, 1 is good

# Sample Co2meter readings
meter1='C569ppm:T69.4F:H63.9%:d56.7F:w61.4F3c'
meter1rex='C\d{3,4}ppm:T\d{2}.\dF:H\d{2}.\d%:d\d{2}.\dF:.\d{2}.\dF\d'
meter1rexrelaxed='C\d{3,4}ppm:T\d{2}.\d'
re.match(meter1rex,meter1)

# there is a blank line after each data line in the reference meter output

meter2='$CO2:Air:RH:DP:WBTf9'
meter2rex='\$CO2:Air:RH:DP:WBTf9'
re.match(meter2rex,meter2)
"""
porttype = ['USB0','USB1','USB2','USB3']
port = porttype[0]
portname = ('/dev/tty'+porttype[0])
#print('Portname ',portname)
sensorname = ['cozir','secondcozir','gps','reference', 'secondcozir','seriallookupbad']
readstatus = ['blank', 'readmore' ,'complete']


fhusb2=''
def readttyUSB2(fhusb2):
    #fhusb2 = serial.Serial('/dev/ttyUSB2', baudrate=9600, bytesize=7,  parity='E', stopbits=2, timeout=3)
    try:
        fhusb2 = serial.Serial('/dev/ttyUSB2', baudrate=9600, bytesize=7,  parity='E', stopbits=2, timeout=3)
    except:
        # print('fhusb2 in the except clause ', fhusb2)
        # if there is no ttyUSB2 then fhusb2 will be False
        # print('fhusb2 ', fhusb2)
        pass
        
    if fhusb2 :
        checkformatch(fhusb2)

# End readttyUSB2

fhusb1=''
def readttyUSB1(fhusb1):
    fhusb1 = serial.Serial('/dev/ttyUSB1', baudrate=9600, bytesize=7,  parity='E', stopbits=2, timeout=3)
    """
    try:
        fhusb1 = serial.Serial('/dev/ttyUSB1', baudrate=9600, bytesize=7,  parity='E', stopbits=2, timeout=3)
    except:
        print('continue')
        #fhusb1 = False
    """    
    usb1data = (fhusb1.readline())
#    print('usb1data ',usb1data)
    # Don't do checkformatch if usb1data is False
    if usb1data :            
        sensorusb1=checkformatch(fhusb1)
        #print('sensorusb1 ',sensorusb1)
        return sensorusb1

# End readttyUSB1

# Notes on serialport reading 12-26-2019
# note use of timeout.
# https://pythonhosted.org/pyserial/shortintro.html
# Seeing good results with GPS using parity='N', stopbits=2
#        and good results with Cozirsensor parity='E'
# ser = serial.Serial('/dev/ttyUSB2',baudrate=9600,bytesize=7, parity='E',stopbits=2, timeout=3)

fhusb0=''
def readttyUSB0(fhusb0):
    fhusb0 = serial.Serial('/dev/ttyUSB0', baudrate=9600, bytesize=7, parity='E', stopbits=2, timeout=3)
    #print('fhusb0 is:',fhusb0)
    #try:
    #    fhusb0 = serial.Serial('/dev/ttyUSB0', baudrate=9600, bytesize=7, parity='E', stopbits=2, timeout=3)
    #except:
    #    print('continue fhusb0 is:',fhusb0)
#    print('fhusb0 is:',fhusb0)
    usb0data = fhusb0.readline()
#    print('usb0data ',usb0data)
        
    # Don't do checkformatch if usb0data is False
    if usb0data:            
        sensor=checkformatch(fhusb0)
        #print('sensor ',sensor)
        return sensor


# end of function

####################################################
# check for match with known sensor data types
# repeat the sensor data lookup if there is a partial match
# identify the kind of data at this usb port
#      if it is GPS data and the GPS is hunting for a fix
#          return the last known good gps data value.
#       if it is co2 meter data, read until the data is complete
#       if it is reference CO2 meter data, read until the CO2 value appears
#           CO2 meter data alternates between meter header and meter values
#

def checkformatch(usbfilehandle):
    #print(' In checkformatch with this filehandle ',usbfilehandle)
    # Use the usbfilehandle and read sensor data
    # When incoming sensor data matches the patterns, 
    #    return that sensor data.
    # Each of the readttyUSBn routines 
    # returns the sensor data. 
    # That is how sensor data gets to the main program without global variables.
    # In Dec 2019 the Reference CO2 meter is not working.
    # so Reference data is not working.
    # There are Python regular expression files like cozirtest
    # that match against the incoming read usb data

    cozirloopcount=1
    cozirloopmax=11
    while cozirloopcount < cozirloopmax :
        usbdata = (usbfilehandle.readline())
        cozirloopcount = cozirloopcount+1
        # print('cozirloopcount ',cozirloopcount)
        # check if this is Cozir sensor data:
        # match code string
        cozirtest=' H \d{5} T \d{5} Z \d{5}'
        matchcoz=re.match(bytes(cozirtest,'UTF-8'), usbdata)
        if matchcoz :       # Cozir sensor data.
            #print('matchcoz-usb cozir ', usbdata,'filehandle',usbfilehandle.port)
            cozirdata = usbdata
            return cozirdata
            #print('cozirdata ',cozirdata)
            cozirloopcount=cozirloopmax
        # Done looking for cozir sensor data.
        # check if this is a GPS full data string and fix is 1 (good)
        # markup for matching process
        gpstest='\$GPGGA,\d{6}.\d{3},\d{4}.\d{4},N,\d{5}.\d{4},W,1'
        matchgps = re.match(bytes(gpstest,'UTF-8'),usbdata)
        # matchgpsfix2 is GPS is on but fix is 2 (not good yet)\
        gpstestfix2='\$GPGGA,\d{6}.\d{3},\d{4}.\d{4},N,\d{5}.\d{4},W,2'
        matchgpsfix2 = re.match(bytes(gpstestfix2,'UTF-8'),usbdata)
        # covers case of GPS is on but data is only first characters
        gpstestgpgga='\$GPGGA'
        matchgpsgpgga = re.match(bytes(gpstestgpgga,'UTF-8'),usbdata)
#        print('inside gps tests ') 
        # if matchgps is true then we have good gps data 
        if matchgps :
            gpsdata = usbdata
            return gpsdata
        #   print('gpsdata ',gpsdata)
            cozirloopcount=cozirloopmax
        # the first kind of incomplete gps data is matchgpsfix2
        if not matchgps : 
#            print('reached not match gps test ') 
            if matchgpsfix2 :
                gpsdata = usbdata
                return gpsdata
                cozirloopcount=cozirloopmax
            #   print('gpsfix2data ',gpsdata)
            #   print('matchgps with fix 2 not yet valid ', matchgpsfix2)
        # the second kind of incomplete gps data is just a few characters
        if not matchgps:
                #print('reached NOT matchgps test ') 
                if matchgpsgpgga :
                #   print('reached match gpsgpgga test ') 
                    gpsdata = usbdata
                    return gpsdata
        

        #print('exit gps ', cozirdata,' ', gpsdata)
    # Reference meter data testing.
    # Reference meter has alternating headings and data values 
        meter1rex='C\d{3,4}ppm:T\d{2}.\dF:H\d{2}.\d%:d\d{2}.\dF:.\d{2}.\dF\d'
        matchref = re.match(bytes(meter1rex,'UTF-8'),usbdata)
        if matchref:
            referencedata = usbdata

    # Reference meter headings
        
        meter2rex='\$CO2:Air:RH:DP:WBTf9'
        matchhdgs = re.match(bytes(meter2rex,'UTF-8'),usbdata)
        # hitting  headings data means read again
        if matchhdgs:                       
            # If the headings are found then read again
            #print('Hit match headings the data is ', usbdata)
            usbdata = (usbfilehandle.readline())
            matchref = re.match(bytes(meter1rex,'UTF-8'),usbdata)
            if matchref :
                return usbdata


        time.sleep(1)
# end of checkformatch


def close_files_atexit():
    print('fhusb0.close()')
#    fhusb1.close()
#    fhusb2.close()
#    fhusb3.close()

def getupcomingtimestamp():
    #Return an integer time modulus 60 seconds that happens in less than 60 seconds
    readcycle= int(60) # Read cycle is an integer number of seconds
    inttime=int(time.time()) 
    # waittime is a future time readcycle + inttime reduced by time already elapsed.
    waittime= int(readcycle - (inttime % readcycle) + inttime)
    #print('inttime ',inttime, 'integertime%60 ', (inttime%60), 'waittime ', waittime)
    return waittime

def makeheader():
    # Put information about the data being collected in '#' fields
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
    #print('Hello there 8')
    return header

def makeadatafilename(timestampinput):
    #Using a time value sent in by another function 
    timestamp=str(timestampinput)
    hostname=socket.gethostname()
    filename=hostname+timestamp+'_'+'co2gps20191229'
    #print('filename ',filename)
    return filename

def cleanlineofdata(sensordata):
    s=str(sensordata)
    #s= s + '\n'
    #print('String before cleanup ',s)
    s=s.replace(',',' ')
    s=s.replace('\\r\\n',' ')
    #print('String after cleanup- ',s)
    return s

def writenewfile(data):
    f1 = open(filename,'a', buffering=1, encoding=None, )
    f1.write(data)
    #print('f1 ',f1)
    return f1

def makefiletimefornextfile(hours):
    print(timet)
    futuretime=timet + hours * 3600
    print("futuretime ",futuretime)
    return futuretime


# Begin main program
#atexit.register(close_files_atexit)
print('Hello there main program')
timestamp=getupcomingtimestamp()
filename=makeadatafilename(timestamp)
#print('filename ',filename)
header=makeheader()
#print('header ',header)
#print('timestamp ',timestamp)
timetoread = int(timestamp -30)
#print('timetoread ',timetoread)
filehandle=writenewfile(header)
#print('filehandle ',filehandle)
timet = int(time.time())
timetmod60 = timet%60
timexplus60 = timet -timet%60 +60
while 1 :
    timet = int(time.time())
    timetmod60 = timet%60
    #timetplus = timet + timetmod60
    #timetplusmod60 = timetplus % 60
    timetminus = timet - timetmod60
    timetminusplus60 = 60 + timet - timetmod60
    timetminusmod60 = timetminus % 60
    timetminusmod60plus60 = 60 + timetminus % 60
    timetminuusmod60plus60mod60 = timetminusmod60plus60 % 60

    #print('top+',timet,'A',timetmod60,'C','D',timetminus,'E',timetminusmod60,'F',timetminuusmod60plus60mod60)
    #print('Test timet == timetminus',timet == timetminus)
    if timet == timetminus :
        print('uggh')
        timeofreadings=timet
        duration=0
        #print('=0 ',timet,' ',timetmod60,' ',timeofreadings,' ',duration)

    #print('Test timet > timetminus',timet > timetminus)
    if timet > timetminus :
        timeofreadings = timetminusplus60
        duration = timet - timetminus
        #print('>30 ',timet,' ',timetmod60,' ',timeofreadings,' ',duration)

    #print('Test timet < timetminus',timet < timetminus)
    if timet < timetminus  :
        timeofreadings = timetminusplus60
        duration=timeminus - timet
        #print('<30 ',timet,' ',timetmod60,' ',timeofreadings,' ',duration)

    #duration of sleep will be 
    print('Sleeping for ',duration,' until ',timeofreadings,' mod ', timeofreadings % 60)
    time.sleep(abs(duration))

    data0=readttyUSB0(fhusb0)
    data1=readttyUSB1(fhusb1)
    #data2=readttyUSB2(fhusb2)
    #print( data0,' ', data1)
    #print('data0 ',data0[0:2])
    #print('data1 ',data1[0:2])

    if data0[0:2] == b' H' :
    #    print(data0,data1)
        sensordata=data0+data1
        #print(sensordata)

    if data0[0:2] == b'$G' :
    #    print(data1,data0)
        sensordata=data1+data0
        #print('rev ',sensordata)

    s=cleanlineofdata(sensordata)
    # add mh placeholder for substituting maidenhead grid square data

    s = str(timeofreadings) +' '+ s +' mh wndkmhr wndbrg \r\n'
    print(s)
    #print('filehandle ',filehandle)
    filehandle.write(s)
    # burn off time to avoid duplicate timestamps
    secondsleft = int(time.time()) -timeofreadings

    #print('Seconds left ',secondsleft)
# End

