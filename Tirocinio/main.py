# Libraries
from pyueye import ueye
import numpy as np
import sys
import camera
import thread_cam as tc
import time
from PIL import Image

# Cameras' id
id = [1, 2, 3]

# Queue of images
queue = []

Lock = True

dev = ["Camera" + str(id[0]), "Camera" + str(id[1]) + "Camera" + str(id[2])]

# Initialize Cameras with specific id
Cam0 = camera.Cam(id[0])
# Cam1 = camera.Cam(id[1])
# Cam2 = camera.Cam(id[2])

# Setup cameras 
Cam0.Setup()
#Cam1.Setup()
#Cam2.Setup()

# Initialize saving threads
#Save_Thread0 = tc.Save_Thread(Cam0, queue)
#Save_Thread1 = tc.Save_Thread(Cam1, queue)
#Save_Thread2 = tc.Save_Thread(Cam2, queue)

# Initialize capture threads
#Capture_Thread0 = tc.Capture_Thread(Cam0, queue)
#Capture_Thread1 = tc.Capture_Thread(Cam1, queue)
#Capture_Thread2 = tc.Capture_Thread(Cam2, queue)

# Continuous capture and saving of the image
try:
    while Cam0.nRet == ueye.IS_SUCCESS: 
    #and Cam1.nRet == ueye.IS_SUCCESS and Cam2.nRet == ueye.IS_SUCCESS:

        if Lock:
            array = ueye.get_data(Cam0.pcImageMemory, Cam0.width, Cam0.height, Cam0.nBitsPerPixel, Cam0.pitch, copy=False)
            # Add the image to the queue
            print(array)
            queue.append(array.copy())
            print("Added to the queue \n")
            Lock = False

        if not Lock:
            if(len(queue)):
                filename = "Camera" + str(Cam0.camID) + "-" + str(time.time())
                array = queue.pop(0)
                reshape = np.reshape(array,(Cam0.height.value, Cam0.width.value, Cam0.bytes_per_pixel))
                img = Image.fromarray(reshape).save("/home/fieldtronics/swim4all/Tirocinio/Photo/" + filename + ".png", "PNG")
                print("Save list \n")
            else:
                print("Not saved \n")
                pass
            Lock = True
    # Starts threads if they are not in a running state
        #if not Capture_Thread0.isRunning:
        #    Capture_Thread0.start()

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
