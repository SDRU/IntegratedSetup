# coding=utf-8
# -*- coding: utf-8 -*-
"""
@author: FLIR and Sandora

This script controls:
    - thermal camera FLIR A655
    
Outputs a real-time maximum temperature from a region of interest

"""

###### USER PARAMETERS
# Region of interest to display temperature
row_low = 10
row_high = 400
col_low = 10
col_high = 500



import os
import PySpin
import sys

sys.path.append("c:/Users/OceanSpectro/Desktop/Sandra/Code/Thermal camera (FLIR)/thermalcamera/")
from CameraFunctions import *



def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()


    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam,row_low, row_high, col_low, col_high)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    return result

if __name__ == '__main__':
    if main():
        # cam.EndAcquisition()
        sys.exit(0)
    else:
        sys.exit(1)
