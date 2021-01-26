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

    def __init__(self, cam, queue, lock):
        super(Save_Thread, self).__init__()
        self.camera = cam
        self.queue = queue
        self.lock = lock
        self.killed = False
        self.isRunning = False
        self.joined = False
        self.t_old = timeit.default_timer()

    def run(self):
        self.isRunning = True

        while not self.killed:
            with self.lock:
                self.joined = True
                self.camera.Save(self.queue)


    def kill(self):
        self.isRunning = False
