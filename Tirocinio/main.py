# Libraries
from pyueye import ueye
import numpy as np
import sys
import camera
import thread_capture as tc
import thread_save as ts
import time
from PIL import Image

# Cameras' id
id = [1, 2, 3]

# Queue of images
queue = []

dev = ["Camera" + str(id[0]), "Camera" + str(id[1]), "Camera" + str(id[2])]

# Initialize Cameras with specific id
Cam0 = camera.Cam(id[0])

# Setup cameras 
Cam0.Setup()

# Initialize saving threads
#Save_Thread0 = ts.Save_Thread(Cam0, queue)

# Initialize capture threads
Capture_Thread0 = tc.Capture_Thread(Cam0, queue)

Capture_Thread0.start()
#Save_Thread0.start()

# Continuous capture and saving of the image
try:
    while Cam0.nRet == ueye.IS_SUCCESS: 
    #and Cam1.nRet == ueye.IS_SUCCESS and Cam2.nRet == ueye.IS_SUCCESS:

        # Starts threads if they are not in a running state
        if not Capture_Thread0.isRunning:
            print("notrunning")

except KeyboardInterrupt:
    # Press Ctrl + C to stop the while loop and kill all the threads
    Capture_Thread0.kill()
    while(Capture_Thread0.isRunning):
        pass
    #Save_Thread0.kill()
    #while(Save_Thread0.isRunning):
    #    pass


# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(Cam0.cam, Cam0.pcImageMemory, Cam0.MemID)

Cam0.exit()
