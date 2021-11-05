# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 16:49:17 2021
@author: Sandora

This script controls:
    - air flow controller Eleveflow OB1

Air in switched ON/OFF in a sequence
"""

from MyFunctions import *


######## USER PARAMETERS
# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2 # where is the air outlet is connected
# sequence parameters
time_on = 2 
time_off = 2
nr_of_repeats = 5


try:
    A = AirObject(channel, pressure_high, pressure_low)        
    
    
    for _ in range(nr_of_repeats):
        A.set_pressure(pressure_high)
        # time.sleep(time_on)
        for i in range(time_on):
            time.sleep(1)
            
        A.set_pressure(pressure_low)
        # time.sleep(time_off)
        for i in range(time_off):
            time.sleep(1)     

            

except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)

    
except KeyboardInterrupt:
    A.close()
    print('Program ended')


except:
    print('Random error')
    A.close()
    