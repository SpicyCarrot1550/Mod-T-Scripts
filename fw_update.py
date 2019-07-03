#!/bin/python
#This script should place the Mod-T into DFU mode and flash the firmware
#Usage: fw_update.py filename.dfu
import sys
import os
import usb.core
import usb.util
import time
import subprocess

#Make sure this script was called correctly
if not len(sys.argv)==2:
    print("Usage: fw_update.py filename.dfu")
    quit()

#Find the Mod-T - we should probably see if it's in DFU mode, too
#That way we can do emergency flashes from recovery mode
dev = usb.core.find(idVendor=0x2b75, idProduct=0x0002)

#If we didn't find a Mod-T we need to throw an error
if dev is None:
    raise ValueError('No Mod-T detected')

#Make sure the filename supplied is actually a file, and error out appropriately
fname=str(sys.argv[1])
if not os.path.isfile(fname):
    print(fname + " not found")
    quit()

#Set active configuration (first is default)
dev.set_configuration()

#First we mimmick the Mod-T desktop utility
#The initial packet is not human readable
#The second packet puts the Mod-T into DFU mode
dev.write(2, bytearray.fromhex('246a0095ff'))
dev.write(2, '{"transport":{"attrs":["request","twoway"],"id":7},"data":{"command":{"idx":53,"name":"Enter_dfu_mode"}}};')

#Wait for the Mod-T to reattach in DFU mode
time.sleep(2)

#Open log file
log = open("/tmp/dfu", "w+")

#Start writing the firmware, and write the output to the log file.
subprocess.popen(["dfu-util", "-d", "2b75:0003", "-a", "0", "-s", "0x0:leave", "-D", fname], stdout=log, stderr=subprocess.STDOUT)

#Loop until the firmware has been written
while True:
    #Steal just the progress value from the file
    tac = subprocess.popen(["tac", "/tmp/dfu"], stdout=PIPE)
    egrep = subprocess.popen(["egrep", "-m", "1", "."], stdin=tac.stdout, stdout=pipe)
    sed = subprocess.popen(["sed", "s/.*[ \t][ \t]*\([0-9][0-9]*\)%.*/\1/"], stdin=egrep.stdout, stdout=PIPE)
    progress = sed.communicate()[0]

    #If dfu-util reports transitioning, we've finished
    if "Transitioning" in progress:
        #We won't always capture the 100% progress indication, so we force it
        progress = 100
        print(progress)
        #exit the loop
        break
    #Write the progress as we get updates
    print(progress)
    #the dfu-util write is kinda slow, let's not waste too much cpu time
    time.sleep(1)

#cleanup our temporary file
log.close()
os.remove /tmp/dfu
