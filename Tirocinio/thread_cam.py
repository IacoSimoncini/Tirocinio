import threading
import camera 
from pyueye import ueye
import numpy as np

Save_Lock = threading.Lock()
Capture_Lock = threading.Lock()

class Save_Thread(threading.Thread):
    def __init__(self, cam, list):
        self.camera = cam
        self.coda = list
        self.killed = False
        self.isRunning = False

    def run(self):
        if self.killed:
            raise SystemExit
        else:
            self.isRunning = True
            Save_Lock.acquire()
            self.camera.Save(self.coda)
            Save_Lock.release()
            self.isRunning = False
    
    def kill(self):
        self.killed = True


class Capture_Thread(threading.Thread):
    def __init__(self, cam, list):
        self.camera = cam
        self.coda = list
        self.killed = False
        self.isRunning = False

    def run(self):
        if self.killed:
            raise SystemExit
        else:
            self.isRunning = True
            Capture_Lock.acquire()
            self.camera = cam.Cature(self.coda)
            Capture_Lock.release()
            self.isRunning = False
        
    def kill(self):
        self.killed = True
