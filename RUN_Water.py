# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 16:49:17 2021
This script runs irrigation in an ON/OFF sequence
@author: Sandora
"""

from StageWaterAirCameraFunctions import *



# USER PARAMETERS

water_jet_setpoint_high = 30 # the value is in %
water_jet_setpoint_low = 0 # the value is in %
time_on = 5
time_off = 5


try:
    I = Irrigation()
    I.set_setpoint(water_jet_setpoint_high)
    
    
    for _ in range(100):
        I.set_setpoint(water_jet_setpoint_high)
        time.sleep(time_on)
        # for i in range(time_on):
        #     time.sleep(1)
            
        I.set_setpoint(water_jet_setpoint_low)
        time.sleep(time_off)
        # for i in range(time_off):
        #     time.sleep(1)        
            
    
except KeyboardInterrupt:
    I.close()
    print('Program ended')
          
except SettingsNotAcceptedError:
    print('Restart the irrigation system')
    
except:
    print('Random error')
    I.close()
    