import threading
import camera 
from pyueye import ueye
import numpy as np

# Lock variables
Save_Lock = threading.Lock()
Capture_Lock = threading.Lock()


class Save_Thread(threading.Thread):
    """ 
    Thread for saving images in png format 
    """

    def __init__(self, cam, list):
        self.camera = cam
        self.queue = list
        self.killed = False
        self.isRunning = False

    def run(self):
        if self.killed:
            raise SystemExit
        else:
            self.isRunning = True
            Save_Lock.acquire()
            self.camera.Save(self.queue)
            Save_Lock.release()
            self.isRunning = False
    
    def kill(self):
        self.killed = True


class Capture_Thread(threading.Thread):
    """ 
    Thread for capturing images
    """

    def __init__(self, cam, list):
        self.camera = cam
        self.queue = list
        self.killed = False
        self.isRunning = False

    def run(self):
        if self.killed:
            raise SystemExit
        else:
            self.isRunning = True
            Capture_Lock.acquire()
            self.camera = cam.Cature(self.queue)
            Capture_Lock.release()
            self.isRunning = False
        
    def kill(self):
        self.killed = True
