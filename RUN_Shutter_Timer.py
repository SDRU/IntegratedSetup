# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 16:03:26 2021

@author: Sandora
"""

from Functions import *
import datetime

duration = 2 # sec

try:
    
    Shutter = ShutterObject(duration)
    
    Shutter.unblock()
    starttime = datetime.datetime.now()
    
    while True: 
        # shutter timer
        if datetime.datetime.now() > (starttime + datetime.timedelta(seconds=Shutter.duration)):  
            Shutter.close()                    
            break
        
except KeyboardInterrupt:
    Shutter.close()
