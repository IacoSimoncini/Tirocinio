import threading
import camera 
from pyueye import ueye
import numpy as np
import time

# Lock variables
Lock = threading.Lock()

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

    def run(self):
        self.isStarted = True
        self.isRunning = True

        while not self.killed:
            start = time.time()
            Lock.acquire()
            self.camera.Capture(self.queue)
            Lock.release()
            end = time.time()
            print("Time Capture Thread: " + str(end - start))

        if self.killed:
            self.isRunning = False
            raise SystemExit
            
        self.isRunning = False

    def kill(self):
        self.killed = True
