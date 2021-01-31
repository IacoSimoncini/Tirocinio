from threading import Thread
import camera 
from pyueye import ueye
import numpy as np
import time
import asyncio
from utility import uEyeException, MemoryInfo, ImageBuffer

class Capture_Thread(Thread):
    """ 
    Thread for capturing images
    """

    def __init__(self, cam, queue):
        super(Capture_Thread, self).__init__()
        self.cam = cam
        self.queue = queue
        self.timeout = 1000
        self.isRunning = True
        self.joined = False
        self.t_old = time.time()
        self.file_param = ueye.IMAGE_FILE_PARAMS()

    def run(self):
        count = 0
        while self.isRunning:
            img_buffer = ImageBuffer()
            self.cam.nRet = ueye.is_WaitForNextImage(self.cam.cam, self.timeout, img_buffer.mem_ptr, img_buffer.mem_id)

            if self.cam.nRet == ueye.IS_SUCCESS:
                mem_info = MemoryInfo(self.cam.cam, img_buffer)
                array = ueye.get_data(img_buffer.mem_ptr, mem_info.width, mem_info.height, mem_info.bits, mem_info.pitch, copy=True)
                self.cam.unlock_seq(img_buffer.mem_id, img_buffer.mem_ptr)
                #self.queue.append(array)
                #print("Len: ", len(self.queue))
                filename = "/home/fieldtronics/swim4all/Tirocinio/Photo/Camera" + str(self.cam.camID) + "-" + str(time.time()) + ".png"
                self.file_param.pwchFileName = filename
                self.file_param.nFiletype = ueye.IS_IMG_PNG
                self.file_param.ppcImageMem = None
                self.file_param.pnImageId = None
                nRet = ueye.is_ImageFile(self.cam.cam, ueye.IS_IMAGE_FILE_CMD_SAVE, self.file_param, ueye.sizeof(self.file_param))
                if nRet != ueye.IS_SUCCESS:
                    print("Save failed.")
                    print("Err_code: ", nRet)
                #print("is_ImageFile: ", nRet)
            else:
                print("Missed frame.")
                print("Err_code: ", self.cam.nRet)
            
            count += 1
            if count == 100:
                t = time.time()
                print("count: ", count)
                print("time: ", t - self.t_old)
                print("FPS: ", count / (t - self.t_old))
                print()

    def kill(self):
        self.isRunning = False

    def isJoined(self):
        self.joined = True