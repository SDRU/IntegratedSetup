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

# # STAGE SETTINGS
# pos1=0 # mm
# pos2=40 # mm
# max_velocity=4 # mm/s

# SHUTTER SETTINGS
duration = 10 # seconds how long is shutter open



from MyFunctions import *






try:
    
    Air, Camera, Water, Shutter = [None, None, None, None]    
    
    # Water = IrrigationObject()
    # Water.set_setpoint(water_jet_setpoint_high)
    
    
    Air = AirObject(channel, pressure_high, pressure_low)    
    Air.set_pressure(pressure_low)    
   
    Shutter = ShutterObject(duration)
    
    Camera = CameraObject(thresholdT, adaptive_threshold)
    Camera.run(Air, Shutter) 
    
    Air.close()
    # Water.close()
    

except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)
    
    for var in [Air, Water, Camera, Shutter]:
        if var != None:
            var.close()    
    
except KeyboardInterrupt:
    print('Program ended')
    
    for var in [Air, Water, Shutter]:
        if var != None:
            var.close()  
          
except SettingsNotAcceptedError:
    print('Restart the irrigation system')
    
except:
    print('Random error')
    
    for var in [Air, Water, Camera, Shutter]:
        if var != None:
            var.close() 