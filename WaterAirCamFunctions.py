# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 16:24:33 2021

@author: Sandora
"""
import sys
sys.path.append("C:\\Users\\OceanSpectro\\Desktop\\Sandra\\Air controller\\SDK_V3_05_03\\Python_64\\DLL64")#add the path of the library here
sys.path.append("C:\\Users\\OceanSpectro\\Desktop\\Sandra\\Air controller\\SDK_V3_05_03\\Python_64") #add the path of the LoadElveflow.py

import pyvisa
import numpy as np
import time
import pandas as pd
from datetime import datetime
import serial
import struct
import os
import PySpin

from serial.tools.list_ports import comports
from email.header import UTF8
from ctypes import *
from array import array
from Elveflow64 import *



class Irrigation:
    def __init__(self):
        # self.water_jet_setpoint_high = water_jet_setpoint_high
        # self.water_jet_setpoint_low = water_jet_setpoint_low
        available_com_ports = comports(include_links=True)
        com_port = None
        for item in available_com_ports:        
            vendor_id = item.vid
            if vendor_id == 10221:
                com_port = comports(include_links=True)[0].device            
                self.ser = serial.Serial(port = com_port, baudrate=9600, rtscts=1, bytesize=8, parity='N', stopbits=2, timeout=1) 
                print('Irrigation initialized')
        if com_port == None:
            raise DeviceNotConnectedError('Irrigation')
        
        
    def add_crc(self,data):
        crc_sum = 0xFFFF
        
        for current_byte in data:
            
            crc_sum = ( crc_sum ^ current_byte << 8 )
            # print(crc_sum)
            for _ in range(8):
                if( crc_sum & 0x8000):
                    
                    # crc_sum <<= 1
                    crc_sum = (crc_sum << 1) ^ 0x1021
                else:
                    crc_sum <<= 1
        low=crc_sum & 0xff
        high = crc_sum  >> 8 & 0xff # this 0xff was my own addition to the code to make it work. Why? Otherwise numbers were too long, so I took only the first byte
    
        lowb = (struct.pack('B',low))
        highb = (struct.pack('B',high))
        message=data + highb + lowb
        return message
    
    
    def read_setpoint(self):
        variable = 37
        message=b'\xfa\x02\x02' + struct.pack('B',variable)
        message=self.add_crc(message)
    
        self.ser.write(message)
        response=self.ser.readline()
        # value in counts
        valuec= struct.unpack('>h',response[2:4])
        # value in %
        valuep =  int((valuec[0] - 400) * 100 / 3300)
        
        return valuep
    
    def set_setpoint(self, valuep):
        variable = 37
        # setpoint value is in %, needs to be converted to counts
        value =  int(( valuep * 3300 /100) + 400)
       
        message = b'\xfa\x04\x01' + struct.pack('B',variable) + struct.pack('>H',value)
        message=self.add_crc(message)
       
        self.ser.write(message)
        response=self.ser.readline()
        
        if response == b'\x00\x01\x00\xff\xad':
            True
        else:
            raise SettingsNotAcceptedError
            
    def close(self):
        self.set_setpoint(0)
        self.ser.close()
        print('Irrigation closed')
        
        
        
        
        
class Air:
    def __init__(self, channel, pressure_high, pressure_low):        
        self.channel = channel
        self.pressure_high = pressure_high
        self.pressure_low = pressure_low
        self.Instr_ID=c_int32()
        error=OB1_Initialization('01C3577F'.encode('ascii'),1,2,4,3,byref(self.Instr_ID))  
        # Set the calibration type as default
        self.Calib=(c_double*1000)()
        Elveflow_Calibration_Default (byref(self.Calib),1000)
       
              
        if error != 0:
            raise DeviceNotConnectedError('Air')
        else:
            print('Air initialized')
            
        
    def set_air_pressure(self, pressure):
        set_channel=c_int32(self.channel) # convert to c_int32
        set_pressure=c_double(float(pressure) )#convert to c_double
        error=OB1_Set_Press(self.Instr_ID.value, set_channel, set_pressure, byref(self.Calib),1000) 
        return error
    
    def close(self):
        self.set_air_pressure(0) 
        error=OB1_Destructor(self.Instr_ID.value)
        print('Air closed')
        
        
 
        
 
    
        
class Camera:
    def __init__(self, thresholdT, adaptive_threshold):
        self.thresholdT = thresholdT
        self.adaptive_threshold = adaptive_threshold
        self.system = PySpin.System.GetInstance()
        
        # Retrieve list of cameras from the system
        cam_list = self.system.GetCameras()
        num_cameras = cam_list.GetSize()    

        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()
            # Release system instance
            self.system.ReleaseInstance()
            print('Not enough cameras!')  
            
            self = None
            raise DeviceNotConnectedError('Camera')
        else:
            print('Number of cameras detected: %d' % num_cameras)              
            self.cam = cam_list[0]
            print('Camera initialized')    

        
            
    def run_camera(self, AirObject):
        """
        This function acts as the body of the example; please see NodeMapInfo example
        for more in-depth comments on setting up cameras.
    
        :param cam: Camera to run on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            # Initialize camera
            self.cam.Init()
    
        
            # Acquire images     
            self.acquire_images(AirObject)
            
            # Deinitialize camera
            self.cam.DeInit()
    
        
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            

        except KeyboardInterrupt as e:
            raise e
            
        
    
    
            
    def acquire_images(self, AirObject):
        try:

            water = 1
            self.cam.BeginAcquisition()
            temperatures = []
    
            while True:
                
                
                image_result = self.cam.GetNextImage()                
    
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
    
                else:
    
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)                  
                    
                    T = self.convert_to_temperature(image_converted)
                    M = np.amax(T)
                    # print(M)
                    
                    if self.adaptive_threshold == 'ON':
                        # adaptive threshold
                        n = 50 # nr of samples to look back at
                        scaling = 0.9  # how much do we scale the threshold
                        if water == 0:
                            temperatures.append(M)
                            if len(temperatures) > n:
                                threshold_old = self.thresholdT
                                self.thresholdT = scaling * np.max(temperatures[-n:])
                                if threshold_old != self.thresholdT:
                                    print(f'Threshold changed to {self.thresholdT}')
                            
                            
                    
                    if M>self.thresholdT:
                        # print(M)
                        if water == 0:                            
                            AirObject.set_air_pressure(AirObject.pressure_low)                            
                            water = 1
    
                    else:
                        if water == 1:
                            AirObject.set_air_pressure(AirObject.pressure_high) 
                            water = 0
                                
                    image_result.Release()   
    
            self.cam.EndAcquisition()
            
        except KeyboardInterrupt as e:
            print('!!!!!!!!How dare you cancelling me!!!!!!!!!!!')
            AirObject.set_air_pressure(0) 
            AirObject.close()
    
            self.cam.EndAcquisition()
            self.cam.DeInit()
            self.close()
            raise e







    def convert_to_temperature(self,image):
        
        y=image.GetWidth()
        x=image.GetHeight()
        image=image.GetData()
        
        IR=np.reshape(image,[x,y]);
        # IR = IR[row_low:row_high,col_low:col_high]
        x = np.shape(IR)[0]
        y = np.shape(IR)[1]
        
    
        # Adding calibration coefficients from software
        # Coefficients for Counts to Radiance
        Cr_0 = -3.42255e-03
        Cr_1 = 5.01980e-07
        I = np.ones([x,y]) # must coincide with desired size in x or y
        r1 = Cr_0*I
        # Coefficients for Radiance to Temperature
        Ct_0 = -6.32251e+01
        Ct_1 = 3.52488e+04
        Ct_2 = -4.55977e+06
        Ct_3 = 5.02369e+08
        Ct_4 = -3.55013e+10
        Ct_5 = 1.42222e+12
        Ct_6 = -2.45221e+13
    
    
        r2 = Cr_1*IR
        R = r1+r2; # Radiance 
        T = Ct_0*np.ones([x,y]) + Ct_1*R + Ct_2*R**2 + Ct_3*R**3 + Ct_4*R**4 + Ct_5*R**5 + Ct_6*R**6
        return T
    
    def close(self):  
        del self.cam 
        self.system.ReleaseInstance() 
        print('Camera closed')
         
        
    
class DeviceNotConnectedError(Exception):
    def __init__(self, device):
        self.device = device
        self.message = f"{self.device} not connected"
        super().__init__(self.message)

    pass            
        
class SettingsNotAcceptedError(Exception):
    print('Irrigation settings not accepted')
    pass