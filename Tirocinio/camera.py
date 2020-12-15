from pyueye import ueye
from PIL import Image
import time
import threading
import numpy as np
import json
from utility import uEyeException

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

    def handle(self):
        return self.cam

    def Setup(self):
        # Setup camera's driver and color mode

        # Starts the driver and establishes the connection to the camera
        self.nRet = ueye.is_InitCamera(self.cam, None)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
        self.nRet = ueye.is_GetCameraInfo(self.cam, self.cInfo)
        if self.nRet != ueye.IS_SUCCESS:
           raise uEyeException(self.nRet)

        # You can query additional information about the sensor type used in the camera
        self.nRet = ueye.is_GetSensorInfo(self.cam, self.sInfo)
        if self.nRet != ueye.IS_SUCCESS:
           raise uEyeException(self.nRet)
        
        self.nRet = ueye.is_SetAutoParameter(self.cam, ueye.IS_SET_ENABLE_AUTO_GAIN, ueye.DOUBLE(1), ueye.DOUBLE(0))
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        self.nRet = ueye.is_SetAutoParameter(self.cam, ueye.IS_SET_ENABLE_AUTO_SHUTTER, ueye.DOUBLE(1), ueye.DOUBLE(0))
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        self.nRet = ueye.is_Exposure(self.cam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, ueye.DOUBLE(10), ueye.sizeof(ueye.DOUBLE(10)))
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
            
        # Set display mode to DIB
        self.nRet = ueye.is_SetDisplayMode(self.cam, ueye.IS_SET_DM_DIB)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        # Set Color Mode to BGR8
        self.nRet = ueye.is_SetColorMode(self.cam, ueye.IS_CM_BGR8_PACKED)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        self.nRet = self.set_aoi_from_json()
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

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
            raise uEyeException(self.nRet)
       
        #Add to Sequence 
        self.nRet = ueye.is_AddToSequence(self.cam , self.pcImageMemory ,  self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        # Enables the queue mode for existing image memory sequences
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        else:
            print("Press Ctrl + C to leave the programm")
            print()

    def free_run_mode(self):
        self.nRet = ueye.is_CaptureVideo(self.cam, ueye.IS_DONT_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
    def set_aoi_from_json(self):
        """
        Set area of interest from config.json file
        """
        with open('/home/fieldtronics/swim4all/Tirocinio/Tirocinio/config.json') as json_file:
            data = json.load(json_file)
            for j in data['config']:
                self.rectAOI.s32Width = ueye.int(j['width'])
                self.rectAOI.s32Height = ueye.int(j['height'])
                self.rectAOI.s32X = ueye.int(j['x'])
                self.rectAOI.s32Y = ueye.int(j['y'])
        
        return ueye.is_AOI(self.cam, ueye.IS_AOI_IMAGE_SET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        
    def Capture(self, queue):
        
        self.nRet = ueye.is_EnableEvent(self.cam, ueye.IS_SET_EVENT_FRAME)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        self.nRet = ueye.is_SetExternalTrigger(self.cam, ueye.IS_SET_TRIGGER_LO_HI)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        # Digitalize an immage and transfers it to the active image memory. In DirectDraw mode the image is digitized in the DirectDraw buffer.
        self.nRet = self.freeze_video()
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        else:
            print("Trigger status: " + str(ueye.IS_GET_TRIGGER_STATUS))
        
        self.nRet = ueye.is_ForceTrigger(self.cam)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        self.nRet = ueye.is_DisableEvent(self.cam, ueye.IS_SET_EVENT_FRAME)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
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

    def freeze_video(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_FreezeVideo(self.cam, wait_param)

    def exit(self):
        if self.cam is not None:
            self.nRet = ueye.is_ExitCamera(self.cam)
        if self.nRet == ueye.IS_SUCCESS:
            self.cam = None
