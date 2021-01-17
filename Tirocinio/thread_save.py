import threading
import camera 
from pyueye import ueye
import thread_capture as tc
import numpy as np
import timeit


class Save_Thread(threading.Thread):
    """ 
    Thread for saving images in png format 
    """

    def __init__(self, cam, list):
        super(Save_Thread, self).__init__()
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
            tc.sem.acquire()
            try:
                self.camera.Save(self.queue)
            finally:
                tc.sem.release()
                

        if self.killed:
            self.isRunning = False
            raise SystemExit

        self.isRunning = False

    def kill(self):
        self.killed = True
