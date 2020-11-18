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

    def run(self):
        Save_Lock.acquire()
        self.camera.Save(self.coda)
        Save_Lock.release()


class Capture_Thread(threading.Thread):
    def __init__(self, cam, list):
        self.camera = cam
        self.coda = list

    def run(self):
        Capture_Lock.acquire()
        self.camera = cam.Cature(self.coda)
        Capture_Lock.release()
