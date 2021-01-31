import threading
import camera 
from pyueye import ueye
import thread_capture as tc
import numpy as np
import time
import cv2

class Save_Thread(threading.Thread):
    """ 
    Thread for saving images in png format 
    """

    def __init__(self, cam, queue):
        super(Save_Thread, self).__init__()
        self.camera = cam
        self.queue = queue
        self.isRunning = False
        self.joined = False

    def run(self):
        self.isRunning = True
        while self.isRunning:
            if(len(self.queue)):
                t_save_old = time.time()
                filename = "/home/fieldtronics/swim4all/Tirocinio/Photo/Camera" + str(self.camera.camID) + "-" + str(time.time()) + ".png"
                array = self.queue.pop(0)
                reshape = np.reshape(array, (self.camera.height.value, self.camera.width.value, self.camera.bytes_per_pixel))
                cv2.imwrite(filename, reshape)
                t_save = time.time()
                print("Salvataggio: ", t_save - t_save_old)
            else:
                pass

    def kill(self):
        self.isRunning = False

    def isJoined(self):
        self.joined = True
