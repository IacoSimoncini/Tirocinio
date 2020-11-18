from pyueye import ueye
from PIL import Image
import time
import threading

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
        self.m_nColorMode = ueye.INT()
        self.nBitsPerPixel
        self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
        self.width = 0
        self.height = 0
        self.nRet = 0
        self.camID = camID
    
    """
    Setup camera's driver and color mode
    """
    def Setup(self):
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
        
        self.nRet = ueye.is_ResetToDefault(self.cam)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_ResetToDefault camera" + str(self.camID) + " ERROR")

        # Set display mode to DIB
        self.nRet = ueye.is_SetDisplayMode(self.cam, ueye.IS_SET_DM_DIB)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_SetDisplayMode camera" + str(self.camID) + " ERROR")

        # Set the auto gain
        self.nRet = ueye.is_SetAutoParameter(self.cam, ueye.IS_SET_ENABLE_AUTO_GAIN, ueye.double(1), ueye.double(0))
        if self.nRet != ueye.IS_SUCCESS:
            print("set_AutoGain camera" + str(self.camID) + " ERROR")
        
        # Set up the right color mode
        if int.from_bytes(self.sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
            # Setup the coor depth to the current windows setting
            ueye.is_GetColorDepth(self.cam, self.nBitsPerPixel, self.m_nColorMode)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print("IS_COLORMODE_BAYER: ", )
            print("\tm_nColorMode: \t\t", self.m_nColorMode)
            print("\tnBitsPerPixel: \t\t", self.nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", self.bytes_per_pixel)
            print()
    
        elif int.from_bytes(self.sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
            # for color camera models use RGB32 mode
            self.m_nColorMode = ueye.IS_CM_BGRA8_PACKED
            self.nBitsPerPixel = ueye.INT(32)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print("IS_COLORMODE_CBYCRY: ",)
            print("\tm_nColorMode: \t\t", self.m_nColorMode)
            print("\tnBitsPerPixel: \t\t", self.nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", self.bytes_per_pixel)
            print()

        elif int.from_bytes(self.sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
            # for color camera models use RGB32 mode
            self.m_nColorMode = ueye.IS_CM_MONO8
            self.nBitsPerPixel = ueye.INT(32)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print("IS_COLORMODE_CBYCRY: ",)
            print("\tm_nColorMode: \t\t", self.m_nColorMode)
            print("\tnBitsPerPixel: \t\t", self.nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", self.bytes_per_pixel)
            print()

        else:
            # for monochrome camera models use Y8 mode
            self.m_nColorMode = ueye.IS_CM_MONO8
            self.nBitsPerPixel = ueye.INT(8)
            self.bytes_per_pixel = int(self.nBitsPerPixel / 8)
            print("else")

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
        else:
            # Makes the specified image memory the active memory
            self.nRet = ueye.is_SetImageMem(self.cam, self.pcImageMemory, self.MemID)
            if self.nRet != ueye.IS_SUCCESS:
                print("is_SetImageMem camera" + str(self.camID) + " ERROR")
            else:
                # Set the desired color mode
                self.nRet = ueye.is_SetColorMode(self.cam, self.m_nColorMode)
    
        # Activates the camera's live video mode (free run mode)
        self.nRet = ueye.is_CaptureVideo(self.cam, ueye.IS_DONT_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_CaptureVideo camera" + str(self.camID) + " ERROR")

        # Enables the queue mode for existing image memory sequences
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_InquireImageMem camera" + str(self.camID) + " ERROR")
        else:
            print("Press q  to leave the programm")

    """
    Set the external trigger and capture the image saving it in the memory.
    The trend of the trigger signal can be changed.
    """
    def Trigger(self):
        # Activates the trigger input. If the camera is on standby, it will exit standby mode and start trigger mode.
        # The function call sets the edge on which an action takes place.
        # When the trigger input is active, is_FreezeVideo() function waits for an input of the trigger signal.

        # Action on high low edge: IS_SET_TRIGGER_HI_LO
        # Action on low high edge: IS_SET_TRIGGER_LO_HI
        # Deactivates trigger: IS_SET_TRIGGER_OFF
        self.nRet = ueye.is_SetExternalTrigger(self.cam, ueye.IS_SET_TRIGGER_LO_HI)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_SetExternalTrigger camera" + str(self.camID) + " ERROR")
        
        


    def Capture(self, list):
        # Digitalize an immage and transfers it to the active image memory. In DirectDraw mode the image is digitized in the DirectDraw buffer.

        # IS_WAIT: The function waits until an image is grabbed. IF the fourfold frame time is exceeded, this is acknowledge with a time otu.
        # IS_DONT_WAIT: The function returns straight away. 
        self.nRet = ueye.is_FreezeVideo(self.cam, ueye.IS_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_FreezeVideo camera" + str(self.camID) + " ERROR")
        else:
            print(ueye.IS_GET_TRIGGER_STATUS)

        # Reads the properties of the allocated image memory
        self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_InquireImageMem camera" + str(self.camID) + " ERROR")
        else:
            array = ueye.get_data(self.pcImageMemory, self.width, self.height, self.nBitsPerPixel, self.pitch)
            list = list + array


    def Save(self, list):
        if(len(list)):
            filename = "Camera" + str(self.camID) + "-" + time.time()
            array = list.pop(0)
            Image.fromarray(array).save(filename + ".png", 'PNG')
        else:
            pass


    """
    Set the exposure.
    """
    def Set_exposure(self, exposure):
        new_exposure = ueye.c_double(exposure)
        
        # Set the exposure time to new_exposure
        self.nRet = ueye.is_Exposure(self.cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, new_exposure, 8)
        if nRet != ueye.IS_SUCCESS:
            print("is_Exposure camera" + str(self.camID) + " ERROR")
