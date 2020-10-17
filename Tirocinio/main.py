# Libraries
from pyueye import ueye
import numpy as np
import cv2
import sys
import setup

# Variables
hCam = ueye.HIDS(0)                         # First camera with the specified camera ID
sInfo = ueye.SENSORINFO()                   # _Structure that fill with sensor's parameters
cInfo = ueye.CAMINFO()                      
pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()
rectAOI = ueye.IS_RECT()
pitch = ueye.INT()
nBitsPerPixel = ueye.INT(24)                # 24: bits per pixel for color mode; take 8 bits per pixel for monochrome
channels = 3                                # 3: channels for color mode(RGB); take 1 channel for monochrome
m_nColorMode = ueye.INT()
bytes_per_pixel = int(nBitsPerPixel / 8)

# Setup camera's driver and color mode
nRet = setup.SetupDriver(hCam, cInfo, sInfo)
setup.SetupColor(sInfo, m_nColorMode, nBitsPerPixel, bytes_per_pixel)

# Can be used to set the size and position of an "area of interest"(AOI) within an image
nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
if nRet != ueye.IS_SUCCESS:
    print("is_AOI ERROR")

width = rectAOI.s32Width
height = rectAOI.s32Height

# Prints out some information about the camera and the sensor
print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
print("Maximum image width:\t", width)
print("Maximum image height:\t", height)
print()

