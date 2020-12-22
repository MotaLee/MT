from .pi_servo import PiServo
from .pi_cam import PiMjpgCam

class MTPiDvc(object):
    def __init__(self,**argkw) -> None:
        self.dvcid=argkw.get('dvcid',0)
        self.name=argkw.get('name','pi_dvc')
        return

    def close(self):
        ''' overrided.'''
        return
    pass
