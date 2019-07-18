#!/usr/bin/python3
# Find files in current directory with 'co2gps52' in their name. 

# Find two files that have 'co2gps52' in their name
# Find two files also Do not have "sent" in their starting 4 characters
# Send the second newest file by email.
# Rename the second newest file "sent.."
#Then send each file, one at a time by email
# Hopefully, rename files
#import emailtoag6cb
import os

# Find two files with a specified string 'co2gps'
filenames=filelist=os.listdir()
for fname in filenames:
    if fname.find('co2gps52') > 0 :
        print(fname.find('co2gps52'), fname)
        fewnames.append(fname)
        print("fewnames ",fewnames," length of fewnames list ", len(fewnames))
        #os.rename( file_name, 'sent'file_name)


#Script based on Corey Schafer youtube video 7-3-2019

import sys
import os
import imghdr
import smtplib
from email.message import EmailMessage

#filename = sys.argv[1:] # script-name filename (of file to be emailed)
#filenames = sys.argv # a list of file names
print("Input filename ",filename)
 
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
#

msg = EmailMessage()
msg['Subject'] = 'Data file'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'ag6cb.lee@gmail.com'
msg.set_content('Data file ')

print('Filename ',filename)


for file in filename:
    with open(file,'r+b') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name  = f.name
        #print("File type ",file_type)

    if file_type == 'jpeg' :
        #print('It is a jpeg file ',file_name)
        msg.add_attachment(file_data,maintype='image', subtype='file_type', filename=file_name) 

    if  file_type != 'jpeg' :
        #print('It is not a jpeg file treaing it like text ',file_name)
        msg.add_attachment(file_data,maintype='application', subtype='octet-stream', filename=file_name) 

# debugging server start like this, comment out ehlo to loginmjbndasq  936
# python3 -m smtpd -c DebuggingServer -n localhost:1025
#print('Filename as of entry into mail routine',filename)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#with smtplib.SMTP('localhost', 1025) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
    smtp.send_message(msg)
    print("Smtp send_message done")
    os.rename(filename, ('sent',filename))
