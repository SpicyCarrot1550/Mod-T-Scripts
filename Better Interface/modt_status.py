#!/usr/bin/env python3

import usb.core #for communicating with the MOD-t
import json #for parsing JSON read from the MOD-t
import pprint #for pretty printing status
import time #for sleeping


# Find a MOD-t usb device
dev = usb.core.find(idVendor=0x2b75, idProduct=0x0002)
# Throw an exception if a MOD-t was not found
if dev is None:
    raise ValueError('MOD-t not found')

# Read pending data from the MOD-t (bulk reads of 64 bytes from endpoint 0x83)
def read_status():
    # Send this to the MOD-t on endpoint 4; this apparently makes it queue the status data
    dev.write(4, '{"metadata":{"version":1,"type":"status"}}')
    # Read 64 bytes of data from endpoint 0x83
    text=''.join(map(chr, dev.read(0x83, 64)))
    fulltext = text
    # Loop until we have the entire status
    while len(text)==64:
        text=''.join(map(chr, dev.read(0x83, 64)))
        fulltext = fulltext + text
    # Parse the JSON and store it as a python dictionary
    return(json.loads(fulltext))


# If __main__, then pretty print status every five seconds
while __name__ == '__main__':
    pprint.pprint(read_status())
    time.sleep(5)
    print('\n\n\n\n') # For readability
