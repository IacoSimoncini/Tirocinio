import threading
import camera 
from pyueye import ueye
import numpy as np
import timeit
import asyncio

sem = asyncio.Semaphore(value=1)

class Capture_Thread(threading.Thread):
    """ 
    Thread for capturing images
    """

    def __init__(self, cam, list):
        super(Capture_Thread, self).__init__()
        self.camera = cam
        self.queue = list
        self.killed = False
        self.isRunning = False
        self.isStarted = False
        self.t_old = timeit.default_timer()

    def run(self):
        self.isStarted = True
        self.isRunning = True
        while not self.killed:
            sem.acquire()
            try:
                self.camera.Capture(self.queue)
                print("Fps: ",self.camera.FPS)
            finally:
                sem.release()

        self.isRunning = False

    def kill(self):
        self.killed = True
