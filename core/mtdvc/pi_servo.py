import time
from .pi_iic import PiIIC
from .pi_SMH import StepperMotorHat
from . import MTPiDvc
class PiServo(MTPiDvc):
    def __init__(self,**argkw):
        super().__init__(argkw)

        self.type=argkw.get('type','MG90')      # MG90 default;
        self.range=argkw.get('range',90)        # Unit as degree;
        self.omega=argkw.get('omega',500)       # Unit as degree/s;
        self.freq=argkw.get('freq',50)          # Unit as Hz;
        self.speed=argkw.get('speed',100)       # Unit as percentage;
        self.pl_min=argkw.get('pl_min',1000)    # Unit as us;
        self.pl_max=argkw.get('pl_max',2000)
        self.mode=argkw.get('mode','iic')
        self.addr=argkw.get('addr',0x6f)
        self.channel=argkw.get('channel',0)

        self.angle=0
        if self.mode=='iic':
            self.host=StepperMotorHat(PiIIC(self.addr))
            self.host.setPWMFreq(self.freq)
        self.num_pl_min=self.pl_min/self.host.pluse_length
        self.num_pl_max=self.pl_max/self.host.pluse_length
        return

    def gotoAgl(self,angle,speed=-1):
        if speed==-1:speed=self.speed
        else:self.speed=speed
        self.angle=angle
        npwm=100/self.speed
        nint=round(npwm)
        ndec=npwm-nint
        if ndec>0:
            dt=(npwm-1)/nint*angle/self.omega
            nint+=1
        else:dt=0
        num_pluse=angle/self.range*(self.num_pl_max-self.num_pl_min)+self.num_pl_min
        # num_pluse=int(num_pluse)
        num_pluse=int(num_pluse//nint)
        for i in range(nint):
            self.host.setPWM(self.channel,0,(i+1)*num_pluse)
            time.sleep(dt)
        # self.host.setPWM(self.channel,0,num_pluse)

        return
    pass
