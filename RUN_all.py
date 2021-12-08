# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:43:14 2021
@author: Sandora

This script controls:
    - irrigation system TESCOM ER5000
    - air flow controller Eleveflow OB1
    - thermal camera FLIR A655
    - shutter Thorlabs SH1 with solenoid controller KSC101
    
Connections to the PC:
    - irrigation system: blue USB-A
    - air flow controller: black USB-A
    - thermal camera: Ethernet cable (directly to PC, not via USB extension!)
    - solenoid controller: special Thorlabs-provided USB-A

Irrigation: always on

Camera: If maximum temperature from the entire image exceeds the thresholdT, air is switched off. Otherwise the air is on and deflects the water jet.
Adaptive threshold: The program looks at maximum temperature from n samples in the past measurements. It makes and average and scales it by scaling factor. 
This value becomes the new treshold temperature.
    
Shutter: Is open for a predefined time

"""

######## USER PARAMETERS

# IRRIGATION SETTINGS
water_pressure = 10 # Water jet pressure. Standard value 30 bars, 0-100 bars accepted

# AIR SETTINGS
air_pressure_high = 2000 # in mbar, 2000 is max, air pressure
air_pressure_low = 0 # anything more than 0 will partially deflect the water jet
channel = 2 # where is the air outlet is connected

# CAMERA SETTINGS
thresholdT = 30 # in degC, treshold temperature to start the irrigation
adaptive_threshold = 'OFF'
# adaptive threshold
n = 50 # nr of samples to look back at
scaling = 0.9  # how much do we scale the thresholdT

# SHUTTER SETTINGS
duration = 10 # in seconds, how long is shutter open. 



from Functions import *


try:
    Air, Camera, Irrigation, Shutter = [None, None, None, None] 
        
    Irrigation = IrrigationObject()
    Irrigation.set_setpoint(water_pressure)
    
    
    Air = AirObject(channel, air_pressure_high, air_pressure_low)    
    Air.set_pressure(air_pressure_low)    
   
    Shutter = ShutterObject(duration)
    
    Camera = CameraObject(thresholdT, adaptive_threshold, n, scaling)
    Camera.run(Air, Shutter)     
    
    # Shutter and Camera are closed automatically when the time is up
    Irrigation.close()
    Air.close()
    
    
    
   
    

except DeviceNotConnectedError as ex:
    close_devices([Air, Irrigation, Camera, Shutter])  
    print('Error: %s' % ex)      
    
except KeyboardInterrupt:    
    close_devices([Air, Irrigation, Camera, Shutter])
    print('Program cancelled')    
          
except SettingsNotAcceptedError:
    close_devices([Air, Irrigation, Camera, Shutter])  
    print('Restart the irrigation system')     
    
except:
    close_devices([Air, Irrigation, Camera, Shutter])  
    print('Random error')