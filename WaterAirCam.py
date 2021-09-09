# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:43:14 2021

@author: Sandora
"""

from WaterAirCamFunctions import *

# IRRIGATION SETTINGS
water_jet_setpoint_high = 30 # the value is in %
# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2
# CAMERA SETTINGS
thresholdT = 30
adaptive_threshold = 'O'


try:
    
    A, C, I = [None, None, None]    
    
    I = Irrigation()
    I.set_setpoint(water_jet_setpoint_high)
    
    
    A = Air(channel, pressure_high, pressure_low)    
    A.set_air_pressure(pressure_high)
    
    
    C = Camera(thresholdT, adaptive_threshold)
    C.run_camera(A)
    
    
    I.close()        
    A.close()
    C.close()
    



except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)  
    
    for var in [A, C, I]:
        if var != None:
            var.close()    
    
except KeyboardInterrupt:
    I.close()
    print('Program ended')
          
except SettingsNotAcceptedError:
    print('Restart the irrigation system')
    
except:
    print('Random error')
    for var in [A, C, I]:
        if var != None:
            var.close() 