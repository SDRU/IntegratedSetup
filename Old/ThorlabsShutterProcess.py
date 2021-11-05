# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 16:30:47 2021

@author: Sandora
"""

from pylablib.devices import Thorlabs
import datetime
import sys

devices = Thorlabs.list_kinesis_devices()
print('Devices found: ',devices)

duration=int(sys.argv[1]) # seconds

class DeviceNotConnectedError(Exception):
    pass

try:
    
    for device in devices:
        serial_nr = device[0]
        if serial_nr.startswith("6"):
            shutter = Thorlabs.kinesis.KinesisDevice(serial_nr)
            shutter.open()
            
        else:
            raise DeviceNotConnectedError

    
    shutter.set_operating_mode(mode=1)    
    # # open shutter once
    shutter.shutter_open()
    starttime = datetime.datetime.now()
    while True:
        if datetime.datetime.now() > (starttime + datetime.timedelta(seconds=duration)):  
            shutter.shutter_close()
            shutter.close()
            break
    
except DeviceNotConnectedError:
    print("No shutter connected")

except KeyboardInterrupt:
    shutter.shutter_close()
    shutter.close()
    print('Interrupted by user')    
        
except:
    shutter.shutter_close()
    shutter.close()
    print('Sth not working here')
    
    
