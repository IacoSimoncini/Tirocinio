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
# Cam1 = camera.Cam(id[1])
# Cam2 = camera.Cam(id[2])

# Setup cameras 
Cam0.Setup()
#Cam1.Setup()
#Cam2.Setup()

# Initialize saving threads
Save_Thread0 = ts.Save_Thread(Cam0, queue)
#Save_Thread1 = ts.Save_Thread(Cam1, queue)
#Save_Thread2 = ts.Save_Thread(Cam2, queue)

# Initialize capture threads
Capture_Thread0 = tc.Capture_Thread(Cam0, queue)
#Capture_Thread1 = tc.Capture_Thread(Cam1, queue)
#Capture_Thread2 = tc.Capture_Thread(Cam2, queue)

Capture_Thread0.start()
Save_Thread0.start()

# Continuous capture and saving of the image
try:
    while Cam0.nRet == ueye.IS_SUCCESS: 
    #and Cam1.nRet == ueye.IS_SUCCESS and Cam2.nRet == ueye.IS_SUCCESS:

    # Starts threads if they are not in a running state
        if not Capture_Thread0.isRunning:
            print("notrunning")
        
        # if not Capture_Thread1.isRunning:
#            Capture_Thread1.start()

        # if not Capture_Thread2.isRunning: 
#            Capture_Thread2.start()

        #if not Save_Thread0.isRunning:
        #    Save_Thread0.start()
#        if not Save_Thread1.isRunning:
 #           Save_Thread1.start()

#        if not Save_Thread2.isRunning:
 #           Save_Thread2.start()

except KeyboardInterrupt:
    # Press Ctrl + C to stop the while loop and kill all the threads
    Capture_Thread0.kill()
#    Capture_Thread1.kill()
 #   Capture_Thread2.kill()

    Save_Thread0.kill()
#    Save_Thread1.kill()
 #   Save_Thread2.kill()


# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(Cam0.cam, Cam0.pcImageMemory, Cam0.MemID)
#ueye.is_FreeImageMem(Cam1.cam, Cam1.pcImageMemory, Cam1.MemID)
#ueye.is_FreeImageMem(Cam2.cam, Cam2.pcImageMemory, Cam2.MemID)

# Disables the hCam camera handle and releases the data structures and memory taken up by the uEye camera
ueye.is_ExitCamera(Cam0.cam)
#ueye.is_ExitCamera(Cam1.cam)
#ueye.is_ExitCamera(Cam2.cam)
