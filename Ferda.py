# SYNC OF THERMAL CAM AND IRRIGATION; IRRIGATION IS ON FOR THE FIRST 10 S THEN IT TURNS ON/OFF DEPENDING ON THE MAX TEMPERATURE DETECTED BY A CAMERA

# USER PARAMS
##############
water_jet_setpoint_high = 30 # the value is in %
water_jet_setpoint_low = 0
thresholdT = 100

row_low = 1
row_high = 400
col_low = 1
col_high = 640


import pyvisa
import numpy as np
import time
import pandas as pd
from datetime import datetime
import serial
import struct
import os
import PySpin
import sys
from FerdaFunctions import *
from serial.tools.list_ports import comports


try:
    available_com_ports = comports(include_links=True)
    for item in available_com_ports:        
        vendor_id = item.vid
        if vendor_id == 10221:
            com_port = comports(include_links=True)[0].device
        
    ser = serial.Serial(port = com_port, baudrate=9600, rtscts=1, bytesize=8, parity='N', stopbits=2, timeout=1) 
    print('Irrigation system initialized')
    
    
    system = PySpin.System.GetInstance()
    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()
    

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        
    else:
        print('Number of cameras detected: %d' % num_cameras)
            
     
    #  Start the irrigation for 10 s in the beginning to prevent carbonization
    set_setpoint(ser, water_jet_setpoint_high)
    time.sleep(10)
    set_setpoint(ser, water_jet_setpoint_low)
        

    # Run example on each camera
    for i, cam in enumerate(cam_list):
        print('Camera started')
        run_single_camera(cam,row_low, row_high, col_low, col_high, ser, water_jet_setpoint_high, water_jet_setpoint_low, thresholdT)
        
    # Release reference to camera
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()    

    # Close serial port for irrigation
    ser.close()
    
except SettingsNotAcceptedError:
    print('Settings were not accepted')
    ser.close()
    cam.EndAcquisition()
    cam.DeInit()
    cam_list.Clear()
    system.ReleaseInstance()    

    
except KeyboardInterrupt:
    print('How dare you cancelling me!')
    set_setpoint(ser, 0)
    print('Jet stopped')
    time.sleep(3)
    ser.close()
    cam.EndAcquisition()
    cam.DeInit()
    cam_list.Clear()
    system.ReleaseInstance()

    
except:
    set_setpoint(ser, 0)
    ser.close()
    cam.EndAcquisition()
    cam.DeInit()
    cam_list.Clear()
    system.ReleaseInstance()
    print('Something went wrong')
