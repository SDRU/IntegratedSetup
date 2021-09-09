# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 14:07:52 2021

@author: Sandra
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 10:47:33 2021

@author: Sandora
"""

import os
import PySpin
import sys
import matplotlib.pyplot as plt
import numpy as np
import struct
import time
import datetime

global temp

def acquire_images(cam, nodemap, nodemap_tldevice, row_low, row_high, col_low, col_high,ser,water_jet_setpoint_high,water_jet_setpoint_low,thresholdT):
    """
    This function acquires and saves 10 images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    try:
        result = True

        water = 0
        cam.BeginAcquisition()


        while True:
            try:
                temperatures=[]
                
                image_result = cam.GetNextImage()                

                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:

                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)                  
                    
                    T = convert_to_temperature(image_converted, row_low,row_high,col_low,col_high)
                    M = np.amax(T)
                    # print(M)
                    
                    n = 40 # nr of samples to look back at
                    scaling = 0.95  # how much do we scale the threshold
                    if water == 0:
                        temperatures.append(M)
                        # print(M)
                        if len(temperatures) > n:
                            thresholdT = scaling * np.max(temperatures[-n:])
                            print(thresholdT)
                    
                    
                    image_result.Release()   

                    # if (datetime.datetime.now() > (starttime + datetime.timedelta(seconds=5))) & (status != 0):
                    
                    if M>thresholdT:
                        print(M)
                        if water == 0:                            
                            set_setpoint(ser, water_jet_setpoint_high)                            
                            water = 1

                    else:
                        if water == 1:
                            set_setpoint(ser, water_jet_setpoint_low) 
                            water = 0
                            
            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False
            
        cam.EndAcquisition()
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False
    
    except KeyboardInterrupt:
        set_setpoint(ser, 0)
        time.sleep(3)
        ser.close()
        cam.EndAcquisition()
        cam.DeInit()
        print('How dare you cancelling me!')

    return result


def run_single_camera(cam,row_low, row_high, col_low, col_high,ser,water_jet_setpoint_high,water_jet_setpoint_low,thresholdT):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images     
        result &= acquire_images(cam, nodemap, nodemap_tldevice,row_low, row_high, col_low, col_high,ser,water_jet_setpoint_high,water_jet_setpoint_low,thresholdT)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False
    except:
        cam.EndAcquisition()
        cam.DeInit()
        result = False

    return result






def convert_to_temperature(image,row_low,row_high,col_low,col_high):
    
    y=image.GetWidth()
    x=image.GetHeight()
    image=image.GetData()
    
    IR=np.reshape(image,[x,y]);
    IR = IR[row_low:row_high,col_low:col_high]
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







class SettingsNotAcceptedError(Exception):
    pass



def add_crc(data):
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


def read_setpoint(ser):
    variable = 37
    message=b'\xfa\x02\x02' + struct.pack('B',variable)
    message=add_crc(message)

    ser.write(message)
    response=ser.readline()
    # value in counts
    valuec= struct.unpack('>h',response[2:4])
    # value in %
    valuep =  int((valuec[0] - 400) * 100 / 3300)
    
    return valuep

def set_setpoint(ser, valuep):
    variable = 37
    # setpoint value is in %, needs to be converted to counts
    value =  int(( valuep * 3300 /100) + 400)
   
    message = b'\xfa\x04\x01' + struct.pack('B',variable) + struct.pack('>H',value)
    message=add_crc(message)
   
    ser.write(message)
    response=ser.readline()
    
    if response == b'\x00\x01\x00\xff\xad':
        # print('Setpoint value was accepted')
        True
    else:
        raise SettingsNotAcceptedError