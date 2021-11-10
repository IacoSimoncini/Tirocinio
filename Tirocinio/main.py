# Libraries
from pyueye import ueye
import asyncio
import camera
import thread_capture as tc
import threading
import os

# Cameras' id
id = [1, 2, 3]

dev = ["Camera" + str(id[0]), "Camera" + str(id[1]), "Camera" + str(id[2])]

# Initialize Cameras with specific id
Cam0 = camera.Cam(id[0], 10)

# Setup cameras 
Cam0.Setup()

p = tc.Capture_Thread(Cam0)
p.start()

# Continuous capture and saving of the image
while Cam0.nRet == ueye.IS_SUCCESS: 
    try:

        if not p.joined:
            p.join()
            print("p joined")

    except KeyboardInterrupt:
        p.kill()
        break

# Releases an image memory that was allocated using is_AllocImageMem() and removes it from the driver management
ueye.is_FreeImageMem(Cam0.cam, Cam0.pcImageMemory, Cam0.MemID)

Cam0.exit()