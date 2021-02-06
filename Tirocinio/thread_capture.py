from threading import Thread
import camera 
from pyueye import ueye
import numpy as np
import time
import asyncio
from utility import MemoryInfo, ImageBuffer, error_log
import datetime
import os

class Capture_Thread(Thread):
    """ 
    Thread for capturing images
    """

    def __init__(self, cam):
        super(Capture_Thread, self).__init__()
        self.cam = cam
        self.timeout = 1000
        self.isRunning = True
        self.joined = False
        self.file_param = ueye.IMAGE_FILE_PARAMS()
        self.x = datetime.datetime.now()
        self.FPS = 0
        self.file = open("/home/pi/swim4all/Tirocinio/Tirocinio/fps.txt", "w")

    def run(self):
        if not os.path.isdir("/home/pi/swim4all/Tirocinio/Photo/" + str(self.x.day) + "-" + str(self.x.month) + "-" + str(self.x.year) + "/"):
            os.makedirs("/home/pi/swim4all/Tirocinio/Photo/" + str(self.x.day) + "-" + str(self.x.month) + "-" + str(self.x.year) + "/")
        
        tempo_conteggio = time.time()

        count = 0

        while self.isRunning:
            t_old = time.time()
            img_buffer = ImageBuffer()
            self.cam.nRet = ueye.is_WaitForNextImage(self.cam.cam, self.timeout, img_buffer.mem_ptr, img_buffer.mem_id)

            if self.cam.nRet == ueye.IS_SUCCESS:
                mem_info = MemoryInfo(self.cam.cam, img_buffer)
                array = ueye.get_data(img_buffer.mem_ptr, mem_info.width, mem_info.height, mem_info.bits, mem_info.pitch, copy=True)
                self.cam.unlock_seq(img_buffer.mem_id, img_buffer.mem_ptr)
                
                if self.cam.mode_filename == 1:
                    filename = "/home/pi/swim4all/Tirocinio/Photo/" + str(self.x.day) + "-" + str(self.x.month) + "-" + str(self.x.year) + "/" + str(self.cam.camID) + "-" + str(time.time()) + ".png"
                else:
                    filename = "/home/pi/swim4all/Tirocinio/Photo/" + str(self.x.day) + "-" + str(self.x.month) + "-" + str(self.x.year) + "/" + str(time.time()) + "-" + str(self.cam.camID) + ".png"
                
                self.file_param.pwchFileName = filename
                self.file_param.nFiletype = ueye.IS_IMG_PNG
                self.file_param.ppcImageMem = None
                self.file_param.pnImageId = None
                nRet = ueye.is_ImageFile(self.cam.cam, ueye.IS_IMAGE_FILE_CMD_SAVE, self.file_param, ueye.sizeof(self.file_param))
                if nRet != ueye.IS_SUCCESS:
                    error_log(nRet, "is_ImageFile")
                    if not self.file.closed:
                        self.file.write("FPS: " + "Salvataggio non riuscito" + "\n") 
                else:
                    t = time.time()
                    self.FPS = 1 / (t - t_old)
                    if not self.file.closed:
                        self.file.write("FPS: " + str(self.FPS) + "\n")
            else:
                error_log(self.cam.nRet, "is_WaitForNextImage")
                if not self.file.closed:
                        self.file.write("FPS: " + "Frame perso" + "\n")
                
            
            count += 1
            if count == 100:
                tempo_fine_conteggio = time.time()
                print("FPS: ", count / (tempo_fine_conteggio - tempo_conteggio))
                print()


    def kill(self):
        self.isRunning = False
        self.file.close()

    def isJoined(self):
        self.joined = True