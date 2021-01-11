from pyueye import ueye
from PIL import Image
import time
import threading
import numpy as np
import json
from utility import uEyeException
import ctypes

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

        self.pixelclock = 0
        self.exposure = 0
        self.width = 0
        self.height = 0
        self.nRet = 0
        self.camID = camID
        self.current_fps = 0

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
        
        # Set Auto Gain
        self.nRet = ueye.is_SetAutoParameter(self.cam, ueye.IS_SET_ENABLE_AUTO_GAIN, ueye.DOUBLE(1), ueye.DOUBLE(0))
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        # Take params from json
        self.param_from_json()

        # Set Pixelclock
        self.set_pixelclock(self.pixelclock)
        
        # Set Exposure
        self.set_exposure(self.exposure)  

        # Set fps
        #self.set_fps(self.current_fps)      

        # Set display mode to DIB
        self.nRet = ueye.is_SetDisplayMode(self.cam, ueye.IS_SET_DM_DIB)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        # Set Color Mode to BGR8
        self.nRet = ueye.is_SetColorMode(self.cam, ueye.IS_CM_BGR8_PACKED)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        # Set AOI
        self.nRet = ueye.is_AOI(self.cam, ueye.IS_AOI_IMAGE_SET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        self.width = self.rectAOI.s32Width
        self.height = self.rectAOI.s32Height

        # Prints out some information about the camera and the sensor
        print("Camera model:\t\t", self.sInfo.strSensorName.decode('utf-8'))
        print("Camera serial no.:\t", self.cInfo.SerNo.decode('utf-8'))
        print("Maximum image width:\t", self.width)
        print("Maximum image height:\t", self.height)
        print("Exposure:\t\t", self.get_exposure())
        print("Frame rate:\t\t", self.current_fps)
        print("PixelClock:\t\t", self.get_pixelclock())
        print()
       
        # Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
        self.nRet = ueye.is_AllocImageMem(self.cam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
       
        # Add to Sequence 
        self.nRet = ueye.is_AddToSequence(self.cam , self.pcImageMemory ,  self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        # Enables the queue mode for existing image memory sequences
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        else:
            print("Press \'Ctrl + C\' to leave the programm")
            print()

    def set_fps(self, fps):
        """
        Set the fps.
        Returns
        =======
        fps: number
            Real fps, can be slightly different than the asked one.
        """
        # checking available fps
        mini, maxi = self.get_fps_range()
        if fps < mini:
            print(f'Warning: Specified fps ({fps:.2f}) not in possible range:'
                  f' [{mini:.2f}, {maxi:.2f}].'
                  f' fps has been set to {mini:.2f}.')
            fps = mini
        if fps > maxi:
            print(f'Warning: Specified fps ({fps:.2f}) not in possible range:'
                  f' [{mini:.2f}, {maxi:.2f}].'
                  f' fps has been set to {maxi:.2f}.')
            fps = maxi
        fps = ueye.c_double(fps)
        new_fps = ueye.c_double()
        self.nRet = ueye.is_SetFrameRate(self.cam, fps, new_fps)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        self.current_fps = float(new_fps)
        return new_fps

    def get_fps_range(self):
        """
        Get the current fps available range.
        Returns
        =======
        fps_range: 2x1 array
            range of available fps
        """
        mini = ueye.c_double()
        maxi = ueye.c_double()
        interv = ueye.c_double()
        self.nRet = ueye.is_GetFrameTimeRange(
                self.cam,
                mini, maxi, interv)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        return [float(1/maxi), float(1/mini)]

    def free_run_mode(self):
        self.nRet = ueye.is_CaptureVideo(self.cam, ueye.IS_DONT_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
    
    def set_pixelclock(self, pixelclock):
        """
        Get the current pixelclock.
        Returns
        =======
        pixelclock: number
            Current pixelclock.
        """
        PCrange = (ctypes.c_uint * 3)()
        self.nRet = ueye.is_PixelClock(self.cam, 
                                        ueye.IS_PIXELCLOCK_CMD_GET_RANGE, 
                                        PCrange,
                                        12)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        pcmin, pcmax, pcincr = PCrange
        if pixelclock < pcmin:
            pixelclock = pcmin
            print(f"Pixelclock out of range [{pcmin}, {pcmax}] and set "
                  f"to {pcmin}")
        elif pixelclock > pcmax:
            pixelclock = pcmax
            print(f"Pixelclock out of range [{pcmin}, {pcmax}] and set "
                  f"to {pcmax}")
        pixelclock = ueye.c_uint(pixelclock)
        self.nRet = ueye.is_PixelClock(self.cam, 
                                        ueye.IS_PIXELCLOCK_CMD_SET,
                                        pixelclock, 4)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

    def set_exposure(self, exposure):
        """
        Set the exposure.
        Returns
        =======
        exposure: number
            Real exposure, can be slightly different than the asked one.
        """
        exposure = ueye.c_double(exposure)
        self.nRet = ueye.is_Exposure(self.cam, 
                                        ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
                                        exposure,
                                        8)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

    def get_exposure(self):
        """
        Get the current exposure.
        Returns
        =======
        exposure: number
            Current exposure.
        """
        exposure = ueye.c_double()
        self.nRet = ueye.is_Exposure(self.cam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE,
                               exposure,  8)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        return exposure

    def get_pixelclock(self):
        """
        Get the current pixelclock.
        Returns
        =======
        pixelclock: number
            Current pixelclock.
        """
        pixelclock = ueye.c_uint()
        self.nRet = ueye.is_PixelClock(self.cam, ueye.IS_PIXELCLOCK_CMD_GET,
                                        pixelclock, 4)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        return pixelclock


    def param_from_json(self):
        """
        Set parameters from config.json file
        """
        with open('/home/fieldtronics/swim4all/Tirocinio/Tirocinio/config.json') as json_file:
            data = json.load(json_file)
            for j in data['config']:
                self.rectAOI.s32Width = ueye.int(j['width'])
                self.rectAOI.s32Height = ueye.int(j['height'])
                self.rectAOI.s32X = ueye.int(j['x'])
                self.rectAOI.s32Y = ueye.int(j['y'])
                self.exposure = j['exp']
                self.pixelclock = j['pixclock']
                self.current_fps = j['fps']
            
    def Capture(self, queue):
        
        self.nRet = ueye.is_EnableEvent(self.cam, ueye.IS_SET_EVENT_FRAME)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        self.nRet = ueye.is_SetExternalTrigger(self.cam, ueye.IS_SET_TRIGGER_LO_HI)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        # Digitalize an immage and transfers it to the active image memory. In DirectDraw mode the image is digitized in the DirectDraw buffer.
        self.nRet = ueye.is_FreezeVideo(self.cam, ueye.IS_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        #self.nRet = ueye.is_ForceTrigger(self.cam)
        #if self.nRet != ueye.IS_SUCCESS:
        #    raise uEyeException(self.nRet)

        self.nRet = ueye.is_DisableEvent(self.cam, ueye.IS_SET_EVENT_FRAME)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)

        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            raise uEyeException(self.nRet)
        
        array = ueye.get_data(self.pcImageMemory, self.width, self.height, self.nBitsPerPixel, self.pitch, copy=False)

        # Add the image to the queue
        #print(array)
        #queue.append(array.copy())
        #print("Added to the queue \n")

    def Save(self, list):
        if(len(list)):
            filename = "Camera" + str(self.camID) + "-" + str(time.time())
            array = list.pop(0)
            reshape = np.reshape(array, (self.height.value, self.width.value, self.bytes_per_pixel))
            Image.fromarray(reshape).save("/home/fieldtronics/swim4all/Tirocinio/Photo/" + filename + ".png", "PNG")
        else:
            pass

    def exit(self):
        if self.cam is not None:
            self.nRet = ueye.is_ExitCamera(self.cam)
        if self.nRet == ueye.IS_SUCCESS:
            self.cam = None
