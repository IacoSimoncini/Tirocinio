import threading
import camera 
from pyueye import ueye
import thread_capture as tc
import numpy as np
import timeit
import time
from PIL import Image

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
        self.t_old = timeit.default_timer()

    def run(self):
        self.isRunning = True
        while self.isRunning:
            if(len(self.queue)):
                t_save_old = timeit.default_timer()
                filename = "Camera" + str(self.camera.camID) + "-" + str(time.time())
                array = self.queue.pop(0)
                reshape = np.reshape(array, (self.camera.height.value, self.camera.width.value, self.camera.bytes_per_pixel))
                Image.fromarray(reshape).save("/home/fieldtronics/swim4all/Tirocinio/Photo/" + filename + ".png", "PNG")
                t_save = timeit.default_timer()
                print("Salvataggio: ", t_save - t_save_old)
            else:
                pass

    def kill(self):
        self.isRunning = False

    def isJoined(self):
        self.joined = True
