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

    def run(self):
        while self.isRunning:
            img_buffer = ImageBuffer()
            self.cam.nRet = ueye.is_WaitForNextImage(self.cam.cam,
                                                     self.timeout,
                                                     img_buffer.mem_ptr,
                                                     img_buffer.mem_id)
            print(self.cam.nRet)
            if self.cam.nRet == ueye.IS_SUCCESS:
                mem_info = MemoryInfo(self.cam.cam, img_buffer)
                array = ueye.get_data(img_buffer.mem_ptr, mem_info.width, mem_info.height, mem_info.bits, mem_info.pitch, copy=True)
                self.cam.unlock_seq(img_buffer.mem_id, img_buffer.mem_ptr)
                self.queue.append(array)
            else:
                print("Missed frame.")
            
            t = time.time()

            FPS = 1/(t - self.t_old)
            print("FPS: ", round(FPS, 2))
            self.t_old = t

    def kill(self):
        self.isRunning = False

    def isJoined(self):
        self.joined = True