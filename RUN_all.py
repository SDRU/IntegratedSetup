# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:43:14 2021

@author: Sandora
"""

######## USER PARAMETERS

# IRRIGATION SETTINGS
water_jet_setpoint_high = 10 # the value is in %

# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2

# CAMERA SETTINGS
thresholdT = 30
adaptive_threshold = 'OFF'

# STAGE SETTINGS
pos1=0 # mm
pos2=40 # mm
max_velocity=4 # mm/s

# SHUTTER SETTINGS
duration = 10 # seconds how long is shutter open



from MyFunctions import *






try:
    
    A, C, I, S, SH = [None, None, None, None, None]    
    
    S = StageProcess(pos1, pos2, max_velocity)
    S.open()
    
    I = Irrigation()
    I.set_setpoint(water_jet_setpoint_high)
    
    
    A = Air(channel, pressure_high, pressure_low)    
    A.set_air_pressure(pressure_low)
    
    SH = ShutterProcess(duration)
    start_command = input("Open the shutter Y/N \n")
    if start_command == "Y":
        SH.open()
    
    C = Camera(thresholdT, adaptive_threshold)
    C.run_camera(A)  
    

except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)
    
    for var in [A, I, S, C, SH]:
        if var != None:
            var.close()    
    
except KeyboardInterrupt:
    print('Program ended')
    
    for var in [A, I, S, SH]:
        if var != None:
            var.close()  
          
except SettingsNotAcceptedError:
    print('Restart the irrigation system')
    S.close()
    
except:
    print('Random error')
    
    for var in [A, I, S, C, SH]:
        if var != None:
            var.close() 