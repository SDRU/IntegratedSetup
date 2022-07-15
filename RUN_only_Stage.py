# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 16:30:47 2021
@author: Sandora and Thorlabs

This script controls:
    - translation stage Thorlabs DDSM50/M
    
    
Runs loop sequence on Thorlabs stage, moving back and forth when the trigger is on.
One trigger pulse is enough to make it move to the next position. 

If you want to find the position range to move, do it manually on the controller first.
If you want to temporarily stop the stage, stop the trigger and the stage will stop either at pos1 or pos2.
If you want to change loop settings, first stop the program with CTRL+C, edit the loop settings and run it again
"""

# USER DEFINED PARAMETERS
# loop settings
pos1=38 # mm
pos2=44 # mm
max_velocity=8 # mm/s




# CONSTANTS
STEP=0.0005 # mm, constant for DDSM50 stage, DO NOT CHANGE!

from pylablib.devices import Thorlabs
import sys
import timeit



sys.path.append("C:\\Users\\Sandra Drusova\\AppData\\Roaming\\Python\\Python38\\site-packages\\pylablib\\devices\\Thorlabs\\")
devices = Thorlabs.list_kinesis_devices()
print('Devices found: ',devices)


for device in devices:
        serial_nr = device[0]
        if serial_nr.startswith("2"):
            stage = Thorlabs.KinesisMotor(serial_nr,scale="step")
            stage.open()


try:
    stage.setup_velocity(max_velocity=int(max_velocity/STEP), acceleration=int(5000/STEP),channel=1, scale='step')
    print(stage.get_velocity_parameters())
   
    # main loop
    stage.move_to(int(pos1/STEP))
    start = timeit.timeit()
    
    while True:

        pos=stage.get_position(channel=1,scale="step")
        if pos==int(pos1/STEP):
            stage.move_to(int(pos2/STEP))
            
        if pos==int(pos2/STEP):
            stage.move_to(int(pos1/STEP))
            
    end = timeit.timeit()
    print(end - start)
    stage.close()
            
except KeyboardInterrupt:
    stage.close()
    print('Interrupted by user')    
        
except:
    stage.close()
    print('Sth not working here')
