# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 16:49:17 2021
@author: Sandora


This script controls:
    - irrigation system TESCOM ER5000
    
Water in switched ON/OFF in a sequence

"""

from MyFunctions import *



######## USER PARAMETERS
# WATER SETTINGS
water_jet_setpoint_high = 30 # the value is in bar
water_jet_setpoint_low = 0 # the value is in bar
# sequence parameters
time_on = 5
time_off = 5
nr_of_repeats = 5


try:
    I = IrrigationObject()
    I.set_setpoint(water_jet_setpoint_high)
    
    
    for _ in range(nr_of_repeats):
        I.set_setpoint(water_jet_setpoint_high)
        # time.sleep(time_on)
        for i in range(time_on):
            time.sleep(1)
            
        I.set_setpoint(water_jet_setpoint_low)
        # time.sleep(time_off)
        for i in range(time_off):
            time.sleep(1)        
     
    I.close()       
    
except KeyboardInterrupt:
    
    I.close()
    print('Program ended')
          
except SettingsNotAcceptedError:
    print('Settings not accepted, restart the irrigation system')
    I.close()
    
except:
    print('Random error')
    I.close()
    