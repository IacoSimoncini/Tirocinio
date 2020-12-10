from pyueye import ueye
from PIL import Image
import time
import threading
import numpy as np

class Cam:
    def __init__(self, camID):
        # Variables
        self.cam = ueye.HIDS(camID)
        self.sInfo = ueye.SENSORINFO()
        self.cInfo = ueye.CAMINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT(24)
        self.channels = 3
        self.m_nColorMode = ueye.IS_CM_RGBA12_UNPACKED
        self.nBitsPerPixel
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)

        self.width = 0
        self.height = 0
        self.nRet = 0
        self.camID = camID

    def Setup(self):
        # Setup camera's driver and color mode
        
        # Starts the driver and establishes the connection to the camera
        self.nRet = ueye.is_InitCamera(self.cam, None)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_initCamera camera" + str(self.camID) + " ERROR")
        
        # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
        self.nRet = ueye.is_GetCameraInfo(self.cam, self.cInfo)
        if self.nRet != ueye.IS_SUCCESS:
           print("is_GetCameraInfo camera" + str(self.camID) + " ERROR")

        # You can query additional information about the sensor type used in the camera
        self.nRet = ueye.is_GetSensorInfo(self.cam, self.sInfo)
        if self.nRet != ueye.IS_SUCCESS:
           print("is_GetSensorInfo camera" + str(self.camID) + " ERROR")
        
        # Set display mode to DIB
        self.nRet = ueye.is_SetDisplayMode(self.cam, ueye.IS_SET_DM_DIB)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_SetDisplayMode camera" + str(self.camID) + " ERROR")

        # Set Color Mode to BGR8
        self.nRet = ueye.is_SetColorMode(self.cam, ueye.IS_CM_BGR8_PACKED)
        if self.nRet != ueye.IS_SUCCESS:
            print("setColorMode camera " + str(self.camID) + " ERROR")

        print("NRET: " + str(self.nRet))
        
        self.nRet = ueye.is_AOI(self.cam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        if self.nRet != ueye.IS_SUCCESS:
            print("is_AOI camera" + str(self.camID) + " ERROR")

        self.width = self.rectAOI.s32Width
        self.height = self.rectAOI.s32Height

        # Prints out some information about the camera and the sensor
        print("Camera model:\t\t", self.sInfo.strSensorName.decode('utf-8'))
        print("Camera serial no.:\t", self.cInfo.SerNo.decode('utf-8'))
        print("Maximum image width:\t", self.width)
        print("Maximum image height:\t", self.height)
        print()

        
        # Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
        self.nRet = ueye.is_AllocImageMem(self.cam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_AllocImageMem camera" + str(self.camID) + " ERROR")
        
        #Add to Sequence 
        self.nRet = ueye.is_AddToSequence(self.cam , self.pcImageMemory ,  self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_AddToSequence ERROR")
    
        # Activates the camera's live video mode (free run mode)
        # self.nRet = ueye.is_CaptureVideo(self.cam, ueye.IS_DONT_WAIT)
        # if self.nRet != ueye.IS_SUCCESS:
        #    print("is_CaptureVideo camera" + str(self.camID) + " ERROR")

        # Set the external trigger and capture the image saving it in the memory
        #self.nRet = ueye.is_SetExternalTrigger(self.cam, ueye.IS_SET_TRIGGER_LO_HI)
        #if self.nRet != ueye.IS_SUCCESS:
        #    print("is_SetExternalTrigger camera" + str(self.camID) + " ERROR")

        self.nRet = ueye.is_CaptureVideo(self.cam, ueye.IS_DONT_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_CaptureVideo Error")

        # Enables the queue mode for existing image memory sequences
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_InquireImageMem camera" + str(self.camID) + " ERROR")
        else:
            print("Press Ctrl + C to leave the programm")
            print()
           

    def Capture(self, queue):
        # Digitalize an immage and transfers it to the active image memory. In DirectDraw mode the image is digitized in the DirectDraw buffer.

        # IS_WAIT: The function waits until an image is grabbed. IF the fourfold frame time is exceeded, this is acknowledge with a time otu.
        # IS_DONT_WAIT: The function returns straight away. 
        """
        self.nRet = ueye.is_FreezeVideo(self.cam, ueye.IS_DONT_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_FreezeVideo camera" + str(self.camID) + " ERROR")
        else:
            print("Trigger status: " + ueye.IS_GET_TRIGGER_STATUS)

        # Reads the properties of the allocated image memory
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_InquireImageMem camera" + str(self.camID) + " ERROR")
        else:
            """
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_InquireImageMem camera" + str(self.camID) + " ERROR")
        
        array = ueye.get_data(self.pcImageMemory, self.width, self.height, self.nBitsPerPixel, self.pitch, copy=False)
        # Add the image to the queue
        print(array)
        queue.append(array.copy())
        print("Added to the queue \n")

    def Save(self, list):
        if(len(list)):
            filename = "Camera" + str(self.camID) + "-" + str(time.time())
            array = list.pop(0)
            reshape = np.reshape(array, (self.height.value, self.width.value, self.bytes_per_pixel))
            Image.fromarray(reshape).save("/home/fieldtronics/swim4all/Tirocinio/Photo/" + filename + ".png", "PNG")
            print("Image saved \n")
        else:
            print("Image not saved \n")
            pass

    def Set_exposure(self, exposure):
        """
        Set the exposure.
        """
        new_exposure = ueye.c_double(exposure)
        
        # Set the exposure time to new_exposure
        self.nRet = ueye.is_Exposure(self.cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, new_exposure, 8)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_Exposure camera" + str(self.camID) + " ERROR")
