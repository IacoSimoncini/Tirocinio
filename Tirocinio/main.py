# Libraries
from pyueye import ueye
import numpy as np
import cv2
import sys
import camera
import thread_cam as tc

id = [0, 1, 2]

coda = []

dev = ["Camera" + str(id[0]), "Camera" + str(id[1]) + "Camera" + str(id[2])]

# Initialize Cameras with specific id
Cam0 = camera.Cam(id[0])
Cam1 = camera.Cam(id[1])
Cam2 = camera.Cam(id[2])

# Setup cameras 
Cam0.Setup()
Cam1.Setup()
Cam2.Setup()

Save_Thread0 = tc.Save_Thread(Cam0, coda)
Save_Thread1 = tc.Save_Thread(Cam1, coda)
Save_Thread2 = tc.Save_Thread(Cam2, coda)

Capture_Thread0 = tc.Capture_Thread(Cam0, coda)
Capture_Thread1 = tc.Capture_Thread(Cam1, coda)
Capture_Thread2 = tc.Capture_Thread(Cam2, coda)

print("isRunning: " + str(Capture_Thread0.isRunning))

# Continuos image display
while Cam0.nRet == ueye.IS_SUCCESS and Cam1.nRet == ueye.IS_SUCCESS and Cam2.nRet == ueye.IS_SUCCESS:

    if Capture_Thread0.isRunning:
        Capture_Thread0.start()
        
    if Capture_Thread1.isRunning:
        Capture_Thread1.start()

    if Capture_Thread2.isRunning: 
        Capture_Thread2.start()

    if Save_Thread0.isRunning:
        Save_Thread0.start()

    if Save_Thread1.isRunning:
        Save_Thread1.start()

    if Save_Thread2.isRunning:
        Save_Thread2.start()
    

    """
    # In order to display the image in an OpenCV window we need to:
    # Extract the data of our image memory
    array0 = ueye.get_data(Cam0.pcImageMemory, Cam0.widht, Cam0.height, Cam0.nBitsPerPixel, Cam0.pitch)
    array1 = ueye.get_data(Cam1.pcImageMemory, Cam1.widht, Cam1.height, Cam1.nBitsPerPixel, Cam1.pitch)
    array2 = ueye.get_data(Cam2.pcImageMemory, Cam2.width, Cam2.height, Cam2.nBitsPerPixel, Cam2.pitch)

    # Reshape date in an numpy array
    frame0 = np.reshape(array0, (Cam0.height.value, Cam0.width.value, Cam0.bytes_per_pixel))
    frame1 = np.reshape(array1, (Cam1.height.value, Cam1.width.value, Cam1.bytes_per_pixel))
    frame2 = np.reshape(array2, (Cam2.height.value, Cam2.width.value, Cam2.bytes_per_pixel))

    # Resize the image by a half
    frame0 = cv2.resize(frame0, (0,0), fx=0.5, fy=0.5)
    frame1 = cv2.resize(frame1, (0,0), fx=0.5, fy=0.5)
    frame2 = cv2.resize(frame2, (0,0), fx=0.5, fy=0.5)

    # Image data processing here


    # Display image 
    cv2.imshow("Camera0 view", frame0)
    cv2.imshow("Camera1 view", frame1)
    cv2.imshow("Camera2 view", frame2)
    # Press q to quit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    """

    

# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(Cam0.cam, Cam0.pcImageMemory, Cam0.MemID)
ueye.is_FreeImageMem(Cam1.cam, Cam1.pcImageMemory, Cam1.MemID)
ueye.is_FreeImageMem(Cam2.cam, Cam2.pcImageMemory, Cam2.MemID)

# Disables the hCam camera handle and releases the data structures and memory taken up by the uEye camera
ueye.is_ExitCamera(Cam0.cam)
ueye.is_ExitCamera(Cam1.cam)
ueye.is_ExitCamera(Cam2.cam)

# Destroys the OpenCV windows
# cv2.destroyAllWindows()


