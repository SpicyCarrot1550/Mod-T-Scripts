#!/bin/bash
#This script actually runs dfu-util to flash firmware to the Mod-T

#Test if the number of arguments is not equal to 1, or the first argument is not a regular file
if [ $# -ne 1 ] || [ ! -f "$1" ]; then
    echo "Usage: flash_firmware.sh PATH_TO_DFU_FILE"
    exit 1
fi

#Actually start writing the firmware, in the background, and log to a file.
dfu-util -d 2b75:0003 -a 0 -s 0x0:leave -D $1 > /tmp/dfu &

#Loop until the firmware has been written
while true; do
	#Steal just the progress value from the file
	progress=`tac /tmp/dfu | egrep -m 1 . | sed 's/.*[ \t][ \t]*\([0-9][0-9]*\)%.*/\1/'`

	#If dfu-util reports transitioning, we've finished
	if [[ $progress == *"Transitioning"* ]]; then
		#We won't always capture the 100% progress indication, so we force it
		progress = 100
		echo $progress
		#exit the loop
		break
	fi
	#Write the progress as we get updates
	echo $progress
	#the dfu-util write is kinda slow, let's not waste too much cpu time
	sleep 1
done

#cleanup our temporary file
rm /tmp/dfu

