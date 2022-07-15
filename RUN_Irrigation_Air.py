# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 15:24:33 2021

@author: Sandora

This script controls:
    - irrigation system TESCOM ER5000
    - air flow controller Eleveflow OB1
    
Connections to the PC:
    - irrigation system: blue USB-A
    - air flow controller: black USB-A
 
It deviates the water jet using air jet in ON/OFF sequence
"""

from Functions import *
import datetime

# WATER SETTINGS
pressure = 30 # in bar
# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2 # where is the air outlet is connected
# sequence parameters
time_on = 0.2 # sec, water jet not deviated
time_off = 0.2 # sec, water jet deviated
nr_of_repeats = 5




try:
    A, I = [None, None]
    I = IrrigationObject()
    A = AirObject(channel, pressure_high, pressure_low)

     
    I.set_setpoint(pressure)
    
    for i in range(nr_of_repeats):
        starttime = datetime.datetime.now()
        print("Irrigation OFF")
        A.set_pressure(pressure_high)
        while True:
            if datetime.datetime.now() > (starttime + datetime.timedelta(seconds=time_off)):  
                break 
        
        starttime = datetime.datetime.now()
        print("Irrigation ON")
        A.set_pressure(pressure_low)
        while True:
            if datetime.datetime.now() > (starttime + datetime.timedelta(seconds=time_on)):  
                break 
    
    I.close()
    A.close()   
    
except KeyboardInterrupt:    
    close_devices([A,I])              
          
except SettingsNotAcceptedError:
    close_devices([A,I])  
    print('Settings not accepted, restart the irrigation system')
    
except DeviceNotConnectedError as ex:
    close_devices([A,I])  
    print('Error: %s' % ex) 
    
except:
    close_devices([A,I])  
    print('Random error')
        


