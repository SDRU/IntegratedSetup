# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 19:49:30 2021

@author: Sandora

This script controls:
    - irrigation system TESCOM ER5000
    - air flow controller Eleveflow OB1
    
Connections to the PC:
    - irrigation system: blue USB-A
    - air flow controller: black USB-A
 
Run the code, it's self explanatory :-)'
"""

from Functions import *

# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2 # where is the air outlet is connected


print("Hello, I am your testing program for irrigation and air! At your service, ready for your input!\n<--------------------->")

try:
    A, I = [None, None]
    I = IrrigationObject()
    A = AirObject(channel, pressure_high, pressure_low) 

    
    while True:
        task = input("How can I help you?\nI set - set irrigation pressure\nA set - set air pressure\nIA seq - start ON/OFF sequence\nexit - stop the jets and this program\n>>>>> ")
                      
        if  task == "I set":
            while True:
                pressure = int(input("How much pressure? Standard value 30 bars, 0-100 bars accepted\n>>>>> "))
                if (pressure in range(0,101)):
                    I.set_setpoint(pressure)
                    print(f"Irrigation pressure successfully set to {pressure} bars")
                    break
                else:
                    print("I'm deeply sorry sir/madam, but I your input is not in the accepted range.")
                    
        elif  task == "A set":
            while True:
                pressure = int(input("How much pressure? Standard value 2000 mbars, 0-2000 mbars accepted\n>>>>> "))
                if (pressure in range(0,2001)):
                    A.set_pressure(pressure)
                    print(f"Air pressure successfully set to {pressure} mbars")
                    break
                else:
                    print("I'm deeply sorry sir/madam, but I your input is not in the accepted range.")
        
        elif task == "IA seq":
            while True:
                pressure = int(input("How much water pressure? Standard value 30 bars, 0-100 bars accepted\n>>>>> "))
                if (pressure in range(0,101)):
                    I.set_setpoint(pressure)
                    print(f"Irrigation pressure successfully set to {pressure} bars")
                    break
                else:
                    print("I'm deeply sorry sir/madam, but I your input is not in the accepted range.")
                    
            while True:
                pressure = int(input("How much air pressure? Standard value 2000 mbars, 0-2000 mbars accepted\n>>>>> "))
                if (pressure in range(0,2001)):
                    A.set_pressure(pressure)
                    print(f"Air pressure successfully set to {pressure} mbars")
                    break
                else:
                    print("I'm deeply sorry sir/madam, but I your input is not in the accepted range.")
                    
            
            
        elif task == "exit":        
            I.close()
            A.close()
            print(">---------------------<")
            print("Always happy to serve you sir/madam!\n")
            break
        
        else:
            print("I'm sorry sir/madam, I am not programmed to understand these commands.")



  
except KeyboardInterrupt:    
    close_devices([A,I])              
    print('Sorry to disturb you sir/madam!\n')
          
except SettingsNotAcceptedError:
    close_devices([A,I])  
    print('Settings not accepted, restart the irrigation system')
    
except DeviceNotConnectedError as ex:
    close_devices([A,I])  
    print('Error: %s' % ex) 
    
except:
    close_devices([A,I])  
    print('Random error')

    

    
    
