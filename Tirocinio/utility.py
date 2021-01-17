from pyueye import ueye
import json
from pyueye import ueye

class uEyeException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code
    def __str__(self):
        return "Err: " + str(self.error_code)

def param_from_json(cam):
    """
    Set parameters from config.json file
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


