# Libraries
from pyueye import ueye
import numpy as np
import cv2
import sys
import setup
import camera

Cam0 = camera.Cam(0)
Cam1 = camera.Cam(1)

Cam0.Setup()
Cam1.Setup()

# Continuos image display
while Cam0.nRet == ueye.IS_SUCCESS && Cam1.nRet == ueye.IS_SUCCESS:

    # In order to display the image in an OpenCV window we need to:
    # Extract the data of our image memory
    array0 = ueye.get_data(Cam0.pcImageMemory, Cam0.widht, Cam0.height, Cam0.nBitsPerPixel, Cam0.pitch)
    array1 = ueye.get_data(Cam1.pcImageMemory, Cam1.widht, Cam1.height, Cam1.nBitsPerPixel, Cam1.pitch)

    # Reshape date in an numpy array
    frame0 = np.reshape(array0, (Cam0.height.value, Cam0.width.value, Cam0.bytes_per_pixel))
    frame1 = np.reshape(array1, (Cam1.height.value, Cam1.width.value, Cam1.bytes_per_pixel))

    # Resize the image by a half
    frame0 = cv2.resize(frame0, (0,0), fx=0.5, fy=0.5)
    frame1 = cv2.resize(frame1, (0,0), fx=0.5, fy=0.5)

    # Image data processing here


    # Display image 
    cv2.imshow("Camera0 view", frame0)
    cv2.imshow("Camera1 view", frame1)

    # Press q to quit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(Cam0.cam, Cam0.pcImageMemory, Cam0.MemID)
ueye.is_FreeImageMem(Cam1.cam, Cam1.pcImageMemory, Cam1.MemID)

# Disables the hCam camera handle and releases the data structures and memory taken up by the uEye camera
ueye.is_ExitCamera(Cam0.cam)
ueye.is_ExitCamera(Cam1.cam)

# Destroys the OpenCV windows
cv2.destroyAllWindows()


