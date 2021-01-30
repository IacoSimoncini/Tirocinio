from threading import Thread
import camera 
from pyueye import ueye
import numpy as np
import timeit
import asyncio
from utility import uEyeException

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

    def run(self):
        while self.isRunning:
            t_old = timeit.default_timer()

            # Digitalize an immage and transfers it to the active image memory. In DirectDraw mode the image is digitized in the DirectDraw buffer.
            self.nRet = ueye.is_FreezeVideo(self.cam.cam, ueye.IS_WAIT)
            if self.nRet != ueye.IS_SUCCESS:
                raise uEyeException(self.nRet)

            t = timeit.default_timer()
            print("FPS: ", 1/(t - t_old))

            array = ueye.get_data(self.cam.pcImageMemory, self.cam.width, self.cam.height, self.cam.nBitsPerPixel, self.cam.pitch, copy=True)

            # Add the image to the queue
            self.queue.append(array)

    def kill(self):
        self.isRunning = False

    def isJoined(self):
        self.joined = True