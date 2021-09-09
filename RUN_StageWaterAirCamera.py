# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 15:43:14 2021

@author: Sandora
"""

######## USER PARAMETERS
# IRRIGATION SETTINGS
water_jet_setpoint_high = 30 # the value is in %
# AIR SETTINGS
pressure_high = 2000 # in mbar
pressure_low = 0
channel = 2
# CAMERA SETTINGS
thresholdT = 50
adaptive_threshold = 'OFF'
# STAGE SETTINGS
pos1=0 # mm
pos2=40 # mm
max_velocity=4 # mm/s




import subprocess
from StageWaterAirCameraFunctions import *
import time


command1 = 'call C:\ProgramData\Anaconda3\Scripts\activate.bat'
command2 = ['py -3.8 "C:/Users/OceanSpectro/Desktop/Sandra/Translation stage/Thorlabs/ThorlabsStageProcess.py"',str(pos1), str(pos2),str(max_velocity)]
command2 = " ".join(command2)
subprocess.Popen(command1,  shell=True)
stage_process = subprocess.Popen(command2,  shell=True)



try:
    
    A, C, I = [None, None, None]    
    
    I = Irrigation()
    I.set_setpoint(water_jet_setpoint_high)
    time.sleep(10)
    
    
    A = Air(channel, pressure_high, pressure_low)    
    A.set_air_pressure(pressure_high)
    
    
    C = Camera(thresholdT, adaptive_threshold)
    C.run_camera(A)
    
    
    I.close()        
    A.close()
    C.close()
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=stage_process.pid))


except DeviceNotConnectedError as ex:
    print('Error: %s' % ex)
    stage_process.kill()
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=stage_process.pid))
    
    for var in [A, C, I]:
        if var != None:
            var.close()    
    
except KeyboardInterrupt:
    stage_process.kill()
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=stage_process.pid))
    I.close()
    print('Program ended')
          
except SettingsNotAcceptedError:
    print('Restart the irrigation system')
    stage_process.kill()
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=stage_process.pid))
    
except:
    print('Random error')
    stage_process.kill()
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=stage_process.pid))
    
    for var in [A, C, I]:
        if var != None:
            var.close() 