# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:43:14 2021
@author: Sandora

This script controls:
    - irrigation system TESCOM ER5000
    - air flow controller Eleveflow OB1
    - thermal camera FLIR A655
    
Connections to the PC:
    - irrigation system: blue USB-A
    - ait flow controller: black USB-A
    - thermal camera: Ethernet cable

Irrigation: always on

Camera: If maximum temperature from the entire image exceeds the thresholdT, air is switched off. Otherwise the air is on and deflects the water jet.
Adaptive threshold: The program looks at maximum temperature from n samples in the past measurements. It makes and average and scales it by scaling factor. 
This value becomes the new treshold temperature.
    
Shutter: Is open for a predefined time

"""

######## USER PARAMETERS

# IRRIGATION SETTINGS
water_jet_setpoint_high = 30 # in bar, 100 is max, water jet pressure

# AIR SETTINGS
pressure_high = 2000 # in mbar, 2000 is max, air pressure
pressure_low = 0 # anything more than 0 will partially deflect the water jet
channel = 2 # where is the air outlet is connected

# CAMERA SETTINGS
thresholdT = 30 # in degC, treshold temperature to start the irrigation
adaptive_threshold = 'OFF'
# adaptive threshold
n = 50 # nr of samples to look back at
scaling = 0.9  # how much do we scale the thresholdT

# SHUTTER SETTINGS
duration = 10 # in seconds, how long is shutter open. 



from Functions_Irrigation_Air_Camera import *


try:
    
    Air, Camera, Water = [None, None, None]    
    
    Water = IrrigationObject()
    Water.set_setpoint(water_jet_setpoint_high)
    
    
    Air = AirObject(channel, pressure_high, pressure_low)    
    Air.set_pressure(pressure_low)    
   
    # Shutter = ShutterObject(duration)
    
    Camera = CameraObject(thresholdT, adaptive_threshold, n, scaling)
    Camera.run(Air) 
    
    Air.close()
    Water.close()
    # Shutter.close()
    

except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)
    
    for var in [Air, Water, Camera]:
        if var != None:
            var.close()    
    
except KeyboardInterrupt:
    print('Program ended')
    
    for var in [Air, Water]:
        if var != None:
            var.close()  
          
except SettingsNotAcceptedError:
    print('Restart the irrigation system')
    
except:
    print('Random error')
    
    for var in [Air, Water, Camera]:
        if var != None:
            var.close() 