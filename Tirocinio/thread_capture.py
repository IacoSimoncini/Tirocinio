from threading import Thread
import camera 
from pyueye import ueye
import numpy as np
import timeit
import asyncio

class Capture_Thread(Thread):
    """ 
    Thread for capturing images
    """

    def __init__(self, cam, queue, lock):
        super(Capture_Thread, self).__init__()
        self.cam = cam
        self.lock = lock
        self.queue = queue
        self.timeout = 1000
        self.isRunning = True
        self.joined = False
        self.t_old = timeit.default_timer()

    def run(self):
        while self.isRunning:
            with self.lock:
                self.joined = True
                self.cam.Capture(self.queue)
                print("FPS: ", self.cam.FPS)

    def kill(self):
        self.isRunning = False

