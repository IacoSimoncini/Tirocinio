import threading
import camera 
from pyueye import ueye
import thread_capture as tc
import numpy as np
import time

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

    def run(self):
        self.isStarted = True
        self.isRunning = True

        while not self.killed:
            start = time.time()
            tc.Lock.acquire()
            self.camera.Save(self.queue)
            tc.Lock.release()
            end = time.time()
            print("Time Save Thread: " + str(end - start))
        
        if self.killed:
            self.isRunning = False
            raise SystemExit

        self.isRunning = False

    def kill(self):
        self.killed = True
