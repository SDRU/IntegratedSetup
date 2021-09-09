# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 16:49:17 2021
This script runs air in an ON/OFF sequence
@author: Sandora
"""

from StageWaterAirCameraFunctions import *


######## USER PARAMETERS
# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2
time_on = 2
time_off = 2


try:
    A = Air(channel, pressure_high, pressure_low)        
    
    
    for _ in range(100):
        A.set_air_pressure(pressure_low)
        time.sleep(time_on)
        # for i in range(time_on):
        #     time.sleep(1)
            
        A.set_air_pressure(pressure_high)
        time.sleep(time_off)
        # for i in range(time_off):
        #     time.sleep(1)     

            

except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)

    
except KeyboardInterrupt:
    A.close()
    print('Program ended')


except:
    print('Random error')
    A.close()
    