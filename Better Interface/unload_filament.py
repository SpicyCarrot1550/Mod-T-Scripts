#!/usr/bin/env python3

import usb.core #for communicating with the MOD-t
import usb.util #for disposing of resources to allow other scripts to access the Mod-t
import time #for sleeping
from modt_status import read_status #for reading the current status from the MOD-t
import pprint #for pretty printing status


# Find a MOD-t usb device
dev = usb.core.find(idVendor=0x2b75, idProduct=0x0002)
# Throw an exception if a MOD-t was not found
if dev is None:
    raise ValueError('MOD-t not found')

def unload_filament():
    # As with the other files, the first packet is not readable; however, the second packet is
    dev.write(2, bytearray.fromhex('246c0093ff'))
    dev.write(2, '{"transport":{"attrs":["request","twoway"],"id":11},"data":{"command":{"idx":51,"name":"unload_initiate"}}};')
    usb.util.dispose_resources(dev) # This releases the Mod-t for use by other scripts

# If __main__, then load filament and pretty print status every five seconds
if __name__ == '__main__':
    unload_filament()
    while True:
        pprint.pprint(read_status())
        time.sleep(5)
        print('\n\n\n\n') # For readability
