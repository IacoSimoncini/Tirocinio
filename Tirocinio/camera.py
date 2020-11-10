import threading
from pyueye import ueye
import setup

class Cam:
    def __init__(self, camID):
        # Variables
        self.cam = ueye.HIDS(camID)
        self.sInfo = ueye.SENSORINFO
        self.cInfo = ueye.CAMINFO
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        self.nBitsPerPixel = ueye.INT(24)
        self.channels = 3
        self.m_nColorMode = ueye.INT()
        self.bytes_per_pixel = int(nBitsPerPixel / 8)
        self.nRet
        self.width
        self.height
    
    # Setup camera's driver and color mode
    def Setup(self):
        # Starts the driver and establishes the connection to the camera
        self.nRet = ueye.is_InitCamera(self.cam, None)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_initCamera ERROR")
        
        # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
        self.nRet = ueye.is_GetCameraInfo(self.cam, self.cInfo)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_GetCameraInfo ERROR")

        # You can query additional information about the sensor type used in the camera
        self.nRet = ueye.is_GetSensorInfo(self.cam, self.sInfo)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_GetSensorInfo ERROR")
        
        self.nRet = ueye.is_ResetToDefault(self.cam)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_ResetToDefault ERROR")
        
        # Set display mode to DIB
        self.nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_SetDisplayMode ERROR")
        
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

        self.nRet = ueye.is_AOI(self.cam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(rectAOI))
        if self.nRet != ueye.IS_SUCCESS:
            print("is_AOI ERROR")

        self.width = rectAOI.s32Width
        self.height = rectAOI.s32Height

        # Prints out some information about the camera and the sensor
        print("Camera model:\t\t", self.sInfo.strSensorName.decode('utf-8'))
        print("Camera serial no.:\t", self.cInfo.SerNo.decode('utf-8'))
        print("Maximum image width:\t", self.width)
        print("Maximum image height:\t", self.height)
        print()

        # Allocates an image memory for an image having its dimensions defined by width and height and its color depth defined by nBitsPerPixel
    self.nRet = ueye.is_AllocImageMem(self.cam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
    if self.nRet != IS_SUCCESS:
        print("is_AllocImageMem ERROR")
    else:
        # Makes the specified image memory the active memory
        self.nRet = ueye.is_SetImageMem(self.cam, self.pcImageMemory, self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_SetImageMem ERROR")
        else:
            # Set the desired color mode
            self.nRet = ueye.is_SetColorMode(self.cam, self.m_nColorMode)
    
    # Activates the camera's live video mode (free run mode)
    self.nRet = ueye.is_CaptureVideo(self.cam, ueye.IS_DONT_WAIT)
    if self.nRet != ueye.IS_SUCCESS:
        print("is_CaptureVideo ERROR")


    # Enables the queue mode for existing image memory sequences
    self.nRet = ueye.is_InquireImageMem(self.cam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
    if self.nRet != ueye.IS_SUCCESS:
        print("is_InquireImageMem ERROR")
    else:
        print("Press q  to leave the programm")
            
        