from pyueye import ueye
import json
from pyueye import ueye
import syslog

class uEyeException(Exception):
    def __init__(self, error_code, name_funct):
        self.error_code = error_code
        self.name = name_funct
    def __str__(self):
        return self.name + ": " + str(self.error_code)

def error_log(error_code, name_funct):
    """
    Writes any errors to the syslog.
    Parameters
    ==========
    error_code: int
        Error value returned by a pyueye function.
    name_funct: str
        Name of the pyueye function.
    """
    syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_ERR)
    syslog.syslog(syslog.LOG_ERR, str(name_funct) + ": " + str(error_code))

def param_from_json(cam):
    """
    Set parameters from config.json file
    Parameter
    =========
    cam: Cam
        IDS camera
    """
    with open('/home/fieldtronics/swim4all/Tirocinio/Tirocinio/config.json') as json_file:
        data = json.load(json_file)
        for j in data['config']:
            cam.rectAOI.s32Width = ueye.int(j['width'])
            cam.rectAOI.s32Height = ueye.int(j['height'])
            cam.rectAOI.s32X = ueye.int(j['x'])
            cam.rectAOI.s32Y = ueye.int(j['y'])
            cam.exposure = j['exp']
            cam.pixelclock = j['pixclock']
            cam.current_fps = j['fps']
            cam.gain = j['gain']
            cam.rGain = j['rGain']
            cam.bGain = j['bGain']
            cam.gGain = j['gGain']
            cam.mode_filename = j['directory_structure']

class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class ImageBuffer:
    def __init__(self):
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()

class MemoryInfo:
    def __init__(self, cam, img_buffer):
        self.x = ueye.int()
        self.y = ueye.int()
        self.bits = ueye.int()
        self.pitch = ueye.int()
        self.img_buff = img_buffer
        rect_aoi = ueye.IS_RECT()
        nRet = ueye.is_AOI(cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

        if nRet != ueye.IS_SUCCESS:
            error_log(nRet, "is_Aoi")

        self.width = rect_aoi.s32Width.value
        self.height = rect_aoi.s32Height.value
        nRet = ueye.is_InquireImageMem(cam, self.img_buff.mem_ptr, self.img_buff.mem_id, self.x, self.y, self.bits, self.pitch)

        if nRet != ueye.IS_SUCCESS:
            error_log(nRet, "is_InquireImageMem")     
