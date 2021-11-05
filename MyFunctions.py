# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 16:24:33 2021

@author: Sandora
"""
import sys
sys.path.append("C:\\Users\\OceanSpectro\\Desktop\\Sandra\\Code\\Air controller (Elveflow)\\SDK_V3_05_03\\Python_64\\DLL64")#add the path of the library here
sys.path.append("C:\\Users\\OceanSpectro\\Desktop\\Sandra\\Code\\Air controller (Elveflow)\\SDK_V3_05_03\\Python_64") #add the path of the LoadElveflow.py

import pyvisa
import numpy as np
import time
import pandas as pd
import datetime
import serial
import struct
import os
import PySpin

from serial.tools.list_ports import comports
from email.header import UTF8
from ctypes import *
from array import array
from Elveflow64 import *
import subprocess
from pylablib.devices import Thorlabs



class IrrigationObject:
    def __init__(self):
        # self.water_jet_setpoint_high = water_jet_setpoint_high
        # self.water_jet_setpoint_low = water_jet_setpoint_low
        available_com_ports = comports(include_links=True)
        com_port = None
        for item in available_com_ports:        
            vendor_id = item.vid
            if vendor_id == 10221:
                com_port = item.device            
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
        
        
        
        
        
class AirObject:
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
            
        
    def set_pressure(self, pressure):
        set_channel=c_int32(self.channel) # convert to c_int32
        set_pressure=c_double(float(pressure) )#convert to c_double
        error=OB1_Set_Press(self.Instr_ID.value, set_channel, set_pressure, byref(self.Calib),1000) 
        return error
    
    def close(self):
        self.set_pressure(0) 
        error=OB1_Destructor(self.Instr_ID.value)
        print('Air closed')
        
        
 
        
 
    
        
class CameraObject:
    def __init__(self, thresholdT, adaptive_threshold,n,scaling):
        self.thresholdT = thresholdT
        self.adaptive_threshold = adaptive_threshold
        self.n = n
        self.scaling = scaling
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
            self.cam = cam_list[0]
            print('Camera initialized')    

        
            
    def run(self, Air, Shutter):
        """
        This function acts as the body of the example; please see NodeMapInfo example
        for more in-depth comments on setting up cameras.
    
        :param cam: Camera to run on.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        # water 1 on, water 0 off
        water = 1 
        temperatures = []
        
        try:
            # Initialize camera  
            self.cam.Init()              
            # Acquire images             
            self.cam.BeginAcquisition()
            
            
            Shutter.unblock()
            starttime = datetime.datetime.now()
            
            while True:                
                
                image_result = self.cam.GetNextImage()                  
                
                # shutter timer
                if datetime.datetime.now() > (starttime + datetime.timedelta(seconds=Shutter.duration)):  
                    Shutter.close()                    
                    image_result.Release() 
                    self.cam.EndAcquisition()
                    self.cam.DeInit()
                    self.close()
                    break
    
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
    
                else:
    
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)                  
                    
                    T = self.convert_to_temperature(image_converted)
                    M = np.amax(T)
                    print(M)
                    
                    if self.adaptive_threshold == 'ON':
                        # adaptive threshold
                        if water == 0:
                            temperatures.append(M)
                            if len(temperatures) > self.n:
                                threshold_old = self.thresholdT
                                self.thresholdT = self.scaling * np.mean(temperatures[-self.n:])
                                if threshold_old != self.thresholdT:
                                    print(f'Threshold changed to {self.thresholdT}')
                            
                            
                    
                    if M>self.thresholdT:
                        # print(M)
                        if water == 0:                            
                            Air.set_pressure(Air.pressure_low)                            
                            water = 1
    
                    else:
                        if water == 1:
                            Air.set_pressure(Air.pressure_high) 
                            water = 0
                                
                    image_result.Release()   
    
            
        except KeyboardInterrupt as e:
            print('!!!!!!!!How dare you cancelling me!!!!!!!!!!!')
    
            self.cam.EndAcquisition()
            self.cam.DeInit()
            self.close()
            raise e

        
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex) 



    def convert_to_temperature(self,image):
        
        try:        
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
        
        except KeyboardInterrupt as e:
            raise e
            
            
    def close(self):  
        del self.cam 
        self.system.ReleaseInstance() 
        print('Camera closed')
        
        
        
class StageProcess:
    def __init__(self,pos1, pos2, max_velocity):
        self.pos1 = pos1
        self.pos2 = pos2
        self.max_velocity = max_velocity
        
        
        
    def open(self):
        command1 = 'call C:\ProgramData\Anaconda3\Scripts\activate.bat'
        command2 = ['py -3.8 "C:/Users/OceanSpectro/Desktop/Sandra/ThorlabsStageProcess.py"',str(self.pos1), str(self.pos2),str(self.max_velocity)]
        command2 = " ".join(command2)
        self.anaconda_prompt = subprocess.Popen(command1,  shell=True)
        self.stage_process = subprocess.Popen(command2)
        print("Stage process started")
        
    def close(self):
        self.stage_process.terminate()    
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.anaconda_prompt.pid))
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.stage_process.pid))
        print('Stage process closed')
        
        
        
        
        
class ShutterObject:
    def __init__(self,duration):
        self.duration = duration         
    
        devices = Thorlabs.list_kinesis_devices()    
        
        if len(devices) == 0:
            raise DeviceNotConnectedError('Shutter')
            
        else:
            for device in devices:
                serial_nr = device[0]
                if serial_nr.startswith("6"):
                    self.shutter = Thorlabs.kinesis.KinesisDevice(serial_nr)
                    self.shutter.open() 
                    self.shutter.set_operating_mode(mode=1)
                    
                else:
                    raise DeviceNotConnectedError('Shutter')
        
        
        
    def block(self):
        self.shutter.shutter_close()
        
    def unblock(self):        
        self.shutter.shutter_open()
        
    def close(self):
        self.block()
        self.shutter.close()
       
        
class ShutterProcess:
    def __init__(self,duration):
        self.duration = duration        
        
        
    def open(self):
        command1 = 'call C:\ProgramData\Anaconda3\Scripts\activate.bat'
        command2 = ['py -3.8 "C:/Users/OceanSpectro/Desktop/Sandra/ThorlabsShutterProcess.py"',str(self.duration)]
        command2 = " ".join(command2)
        self.anaconda_prompt = subprocess.Popen(command1,  shell=True)
        self.shutter_process = subprocess.Popen(command2)
        print("Shutter process started")
        
    def close(self):
        self.shutter_process.terminate()    
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.anaconda_prompt.pid))
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.shutter_process.pid))
        print('Shutter process closed')
         
        
    
class DeviceNotConnectedError(Exception):
    def __init__(self, device):
        self.device = device
        self.message = f"{self.device} not connected"
        super().__init__(self.message)

    pass            
        
class SettingsNotAcceptedError(Exception):
    pass