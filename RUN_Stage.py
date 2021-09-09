# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 16:30:47 2021
Runs loop sequence on Thorlabs stage
@author: Sandora
"""

# USER DEFINED PARAMETERS
pos1=5 # mm
pos2=15 # mm
max_velocity=4 # mm/s

# CONSTANTS
STEP=0.0005 # mm, constant for this stage!





from pylablib.devices import Thorlabs
import sys


sys.path.append("C:\\Users\\OceanSpectro\\AppData\\Roaming\\Python\\Python38\\site-packages\\pylablib\\devices\\Thorlabs\\")
print('Device found: ',Thorlabs.list_kinesis_devices())

stage = Thorlabs.KinesisMotor(Thorlabs.list_kinesis_devices()[0][0],scale="step")
stage.open()



try:
    stage.setup_velocity(max_velocity=int(max_velocity/STEP), channel=1, scale='step')
    
    # Set general trigger parameters
    trin_mode=b'\x03' 
    trin_polarity=b'\x01'
    trout_mode=b'\x00'
    trout_polarity=b'\x00'
    
    stage.set_trigger_params(trin_mode=trin_mode,trin_polarity=trin_polarity,trout_mode=trout_mode,trout_polarity=trout_polarity)
    
    
    # ABSOLUTE MOVE WITH ONLY ONE TRIGGER
    # main loop
    stage.move_to(int(pos1/STEP))
    
    while True:
        pos=stage.get_position(channel=1)
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
