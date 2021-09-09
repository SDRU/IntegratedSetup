# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 16:30:47 2021
Runs Loop sequence on Thorlabs stage
@author: Sandora
"""

from pylablib.devices import Thorlabs
import sys

sys.path.append("C:\\Users\\OceanSpectro\\AppData\\Roaming\\Python\\Python38\\site-packages\\pylablib\\devices\\Thorlabs\\")
STEP=0.0005 # mm, constant for this stage!

devices = Thorlabs.list_kinesis_devices()
print('Devices found: ',devices)


for device in devices:
        serial_nr = device[0]
        if serial_nr.startswith("2"):
            stage = Thorlabs.KinesisMotor(serial_nr,scale="step")
            stage.open()


pos1=int(sys.argv[1]) # mm
pos2=int(sys.argv[2]) # mm
max_velocity=int(sys.argv[3]) # mm/s

try:
    stage.setup_velocity(max_velocity=int(max_velocity/STEP), channel=1, scale='step')
    
    # Set general trigger parameters
    trin_mode=b'\x03' 
    trin_polarity=b'\x01'
    trout_mode=b'\x00'
    trout_polarity=b'\x00'
    
    stage.set_trigger_params(trin_mode=trin_mode,trin_polarity=trin_polarity,trout_mode=trout_mode,trout_polarity=trout_polarity)
    
    
    # ABSOLUTE MOVE WITH ONLY ONE TRIGGER
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
