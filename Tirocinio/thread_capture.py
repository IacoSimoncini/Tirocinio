import threading
import camera 
from pyueye import ueye
import numpy as np
import timeit

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
        self.t_old = timeit.default_timer()

    def run(self):
        self.isStarted = True
        self.isRunning = True

        while not self.killed:
            Lock.acquire()
            try:
                self.camera.Capture(self.queue)
            finally:
                Lock.release()
            t = timeit.default_timer()
            fps = 1/(t - self.t_old)
            self.t_old = t
            print("Fps: ", round(fps, 2))

        if self.killed:
            self.isRunning = False
            raise SystemExit

        self.isRunning = False

    def kill(self):
        self.killed = True
