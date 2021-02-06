from pyueye import ueye
from PIL import Image
import time
import threading
import numpy as np
import json
from utility import param_from_json, Rect, ImageBuffer, MemoryInfo, error_log
import ctypes
import timeit

bits_per_pixel = {ueye.IS_CM_SENSOR_RAW8: 8,
                  ueye.IS_CM_SENSOR_RAW10: 16,
                  ueye.IS_CM_SENSOR_RAW12: 16,
                  ueye.IS_CM_SENSOR_RAW16: 16,
                  ueye.IS_CM_MONO8: 8,
                  ueye.IS_CM_RGB8_PACKED: 24,
                  ueye.IS_CM_BGR8_PACKED: 24,
                  ueye.IS_CM_RGBA8_PACKED: 32,
                  ueye.IS_CM_BGRA8_PACKED: 32,
                  ueye.IS_CM_BGR10_PACKED: 32,
                  ueye.IS_CM_RGB10_PACKED: 32,
                  ueye.IS_CM_BGRA12_UNPACKED: 64,
                  ueye.IS_CM_BGR12_UNPACKED: 48,
                  ueye.IS_CM_BGRY8_PACKED: 32,
                  ueye.IS_CM_BGR565_PACKED: 16,
                  ueye.IS_CM_BGR5_PACKED: 16,
                  ueye.IS_CM_UYVY_PACKED: 16,
                  ueye.IS_CM_UYVY_MONO_PACKED: 16,
                  ueye.IS_CM_UYVY_BAYER_PACKED: 16,
                  ueye.IS_CM_CBYCRY_PACKED: 16}
                  

class Cam:
    def __init__(self, camID, buffer_count=3):
        # Variables
        self.cam = ueye.HIDS(camID)
        self.sInfo = ueye.SENSORINFO()
        self.cInfo = ueye.CAMINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT(8)
        self.channels = 3
        self.m_nColorMode = ueye.IS_CM_SENSOR_RAW8
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
        self.buffer_count = buffer_count
        self.img_buffer = []
        self.mode_filename = 0

        self.pixelclock = 0
        self.exposure = 0
        self.width = 0
        self.height = 0
        self.nRet = 0
        self.camID = camID
        self.current_fps = 0
        self.FPS = 0
        self.gain = 0
        self.rGain = 0
        self.bGain = 0
        self.gGain = 0
        
    def handle(self):
        return self.cam

    def Setup(self):
        # Setup camera's driver and color mode

        # Starts the driver and establishes the connection to the camera
        self.nRet = ueye.is_InitCamera(self.cam, None)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_InitCamera")
        
        self.nRet = ueye.is_SetExternalTrigger(self.cam, ueye.IS_SET_TRIGGER_LO_HI)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_SetExternalTrigger") 

        # You can query additional information about the sensor type used in the camera
        self.nRet = ueye.is_GetSensorInfo(self.cam, self.sInfo)
        if self.nRet != ueye.IS_SUCCESS:
           error_log(self.nRet, "is_GetSensorInfo")

        # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
        self.nRet = ueye.is_GetCameraInfo(self.cam, self.cInfo)
        if self.nRet != ueye.IS_SUCCESS:
           error_log(self.nRet, "is_GetCameraInfo")

        # Set Auto Gain
        #self.set_gain_auto(1)

        # Take params from json
        param_from_json(self)

        # Set Gain
        self.set_gain(self.gain, self.rGain, self.gGain, self.bGain)
        
        # Set Pixelclock
        self.set_pixelclock(self.pixelclock)
        
        # Set Exposure
        self.set_exposure(self.exposure)    

        # Set display mode to DIB
        self.nRet = ueye.is_SetDisplayMode(self.cam, ueye.IS_SET_DM_DIB)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_SetDisplayMode")

        self.get_bit_per_pixel(self.m_nColorMode)

        # Set Color Mode to BGR8
        self.nRet = ueye.is_SetColorMode(self.cam, self.m_nColorMode)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_SetColorMode")

        # Set AOI
        self.nRet = ueye.is_AOI(self.cam, ueye.IS_AOI_IMAGE_SET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_AOI")

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
        print("Gain:\t\t\t", self.get_gain())
        print("rGain:\t\t\t", self.rGain)
        print("bGain:\t\t\t", self.bGain)
        print("gGain:\t\t\t", self.gGain)
        print("Color mode:\t\t", self.m_nColorMode)
        print("Bits per pixel:\t\t", int(self.bits_per_pixel))
        print()

        self.alloc()

        self.nRet = self.capture_video()
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_CaptureVideo")

        print("Press \'Ctrl + C\' to leave the programm")
        print()

    def capture_video(self, wait=True):
        """
        Begin capturing a video in trigger mode (wait=True) or free run (wait=False).
        Parameters
        ==========
        wait: boolean
           To wait or not for the camera frames (default to True).
        """
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_CaptureVideo(self.cam, wait_param)

    def set_gain(self, mGain, rGain, gGain, bGain):
        """
        Set gain

        Params
        ======
        mGain: integer
            master gain value
        rGain: integer
            red gain value, default value 0
        gGain: integer
            green gain value, default value 0
        bGain: integer
            blue gain value, default value 0
        """
        self.nRet = ueye.is_SetHardwareGain(self.cam, 
                                            mGain, 
                                            rGain, 
                                            gGain,
                                            bGain)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_SetHardwareGain")
    
    def get_bit_per_pixel(self, color_mode):
        """
        Returns the number of bits per pixel for the given color mode.
        """
        if color_mode not in bits_per_pixel.keys():
            print(f"Unknown color mode: {color_mode}")
            print("It will be set to default value")
            self.bits_per_pixel = ueye.INT(bits_per_pixel[11])
            self.m_nColorMode = ueye.IS_CM_SENSOR_RAW8
        else:
            self.bits_per_pixel = ueye.INT(bits_per_pixel[color_mode])
            
        
    def get_gain(self):
        """
        Get the current gain.
        Returns
        =======
        gain: number
            Current gain
        """
        self.gain = ueye.is_SetHardwareGain(self.cam, 
                                            ueye.IS_GET_MASTER_GAIN, 
                                            ueye.IS_IGNORE_PARAMETER, 
                                            ueye.IS_IGNORE_PARAMETER,
                                            ueye.IS_IGNORE_PARAMETER)
        return self.gain 

    def get_aoi(self):
        """
        Get the current area of interest.
        Returns
        =======
        rect: Rect object
            Area of interest
        """
        ueye.is_AOI(self.cam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))
        return Rect(self.rectAOI.s32X.value,
                    self.rectAOI.s32Y.value,
                    self.rectAOI.s32Width.value,
                    self.rectAOI.s32Height.value)

    def set_gain_auto(self, toggle):
        """
        Set/unset auto gain.
        Params
        ======
        toggle: integer
            1 activate the auto gain, 0 deactivate it
        """
        value = ueye.c_double(toggle)
        value_to_return = ueye.c_double()
        self.nRet = ueye.is_SetAutoParameter(self.cam,
                                    ueye.IS_SET_ENABLE_AUTO_GAIN,
                                    value,
                                    value_to_return)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_SetAutoParameter")

    def get_framerate(self):
        """
        Get frame rate.
        Only in free run mode.
        """
        new_fps = ueye.c_double(self.current_fps)
        self.nRet = ueye.is_GetFramesPerSecond(self.cam, new_fps)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_GetFramesPerSecond")
        print(new_fps.value)

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
            error_log(self.nRet, "is_SetFrameRate")
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
            error_log(self.nRet, "is_GetFrameTimeRange")
        return [float(1/maxi), float(1/mini)]
    
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
            error_log(self.nRet, "is_PixelClock")
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
            error_log(self.nRet, "is_PixelClock")

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
            error_log(self.nRet, "is_Exposure")

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
            error_log(self.nRet, "is_Exposure")
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
            error_log(self.nRet, "is_PixelClock")
        return pixelclock

    def trigger_miss(self):
        """
        Check if a trigger miss event occurs.
        """
        error_code = ueye.is_CameraStatus(self.cam, 
                                            ueye.IS_TRIGGER_MISSED,
                                            ueye.IS_GET_STATUS)
        print("error_code: ",error_code)
        
    def unlock_seq(self, mem_id, mem_ptr):
        self.nRet = ueye.is_UnlockSeqBuf(self.cam, mem_id, mem_ptr)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_UnlockSeqBuf")

    def alloc(self):
        """
        Allocate memory for futur images.
        """
        rect = self.get_aoi()
        bpp = self.nBitsPerPixel

        for buff in self.img_buffer:
            self.nRet = ueye.is_FreeImageMem(self.cam, buff.mem_ptr, buff.mem_id)
            if self.nRet != ueye.IS_SUCCESS:
                error_log(self.nRet, "is_FreeImageMem")
        
        self.img_buffer = []

        for i in range(self.buffer_count):
            buff = ImageBuffer()
            ueye.is_AllocImageMem(self.cam,
                                  rect.width,
                                  rect.height,
                                  bpp,
                                  buff.mem_ptr,
                                  buff.mem_id)
            ueye.is_AddToSequence(self.cam, buff.mem_ptr, buff.mem_id)
            self.img_buffer.append(buff)

        self.nRet = ueye.is_InitImageQueue(self.cam, 0)
        if self.nRet != ueye.IS_SUCCESS:
            error_log(self.nRet, "is_InitImageQueue")


    def capture_status(self):
        """
        Check capture status.
        Returns
        =======
        nRet: integer
            Capture status.
        """
        info = ueye.c_uint()
        nRet = ueye.is_CaptureStatus(self.cam, 
                                          ueye.IS_CAPTURE_STATUS_INFO_CMD_GET,
                                          info,
                                          ueye.sizeof(info))
        return nRet

    def exit(self):
        """
        Close camera connection.
        """
        if self.cam is not None:
            self.nRet = ueye.is_ExitCamera(self.cam)
        if self.nRet == ueye.IS_SUCCESS:
            self.cam = None
        print()
        print("Camera exit.")
