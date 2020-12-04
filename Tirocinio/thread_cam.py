import threading
import camera 
from pyueye import ueye
import numpy as np

# Lock variables
Lock = threading.Lock()


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

    def run(self):
        if self.killed:
            raise SystemExit
        else:
            self.isRunning = True
            Lock.acquire()
            self.camera.Save(self.queue)
            Lock.release()
    
    def kill(self):
        self.killed = True


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

    def run(self):
        if self.killed:
            raise SystemExit
        else:
            self.isRunning = True
            Lock.acquire()
            self.camera.Capture(self.queue)
            Lock.release()
        
    def kill(self):
        self.killed = True
