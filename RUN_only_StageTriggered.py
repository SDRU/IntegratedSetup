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
pos1=5 # mm
pos2=15 # mm
max_velocity=4 # mm/s




# CONSTANTS
STEP=0.0005 # mm, constant for DDSM50 stage, DO NOT CHANGE!

from pylablib.devices import Thorlabs
import sys


sys.path.append("C:\\Users\\OceanSpectro\\AppData\\Roaming\\Python\\Python38\\site-packages\\pylablib\\devices\\Thorlabs\\")
devices = Thorlabs.list_kinesis_devices()
print('Devices found: ',devices)


for device in devices:
        serial_nr = device[0]
        if serial_nr.startswith("2"):
            stage = Thorlabs.KinesisMotor(serial_nr,scale="step")
            stage.open()


try:
    stage.setup_velocity(max_velocity=int(max_velocity/STEP), channel=1, scale='step')
    
    # Set general trigger parameters
    tr1_mode=b'\x03' 
    tr1_polarity=b'\x01'
    tr2_mode=b'\x00'
    tr2_polarity=b'\x00'
    
    stage.set_trigger_params(tr1_mode=tr1_mode,tr1_polarity=tr1_polarity,tr2_mode=tr2_mode,tr2_polarity=tr2_polarity)
    
    
    # ABSOLUTE MOVE WITH ONLY ONE TRIGGER
    # main loop
    stage.move_to(int(pos1/STEP))
    
    while True:
        pos=stage.get_position(channel=1,scale="step")
        if pos==int(pos1/STEP):
            stage.set_triggerin_abs_move(position = int(pos2/STEP))
            
        if pos==int(pos2/STEP):
            stage.set_triggerin_abs_move(position = int(pos1/STEP))
    
    stage.close()
            
except KeyboardInterrupt:
    stage.close()
    print('Interrupted by user')    
        
except:
    stage.close()
    print('Sth not working here')
