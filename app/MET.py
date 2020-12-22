import sys,os,time
sys.path.append(os.getcwd())
import core as c
from core import mtnet,mtdvc
class MET(object):
    def __init__(self):
        self.name='Lan'
        self.header='[MET '+self.name+'] '
        self.FLAG_EXIT=False
        self.dvcs=dict()
        self.queue_mc_send=list()
        self.queue_mc_recv=list()
        sro1=mtdvc.PiServo(dvcname='sro1',channel=0)
        sro2=mtdvc.PiServo(dvcname='sro2',channel=1)
        cam1=mtdvc.PiMjpgCam(dvcname='cam1',addr=0,port=8080)
        cam2=mtdvc.PiMjpgCam(dvcname='cam2',addr=1,port=8081)
        self.client=mtnet.MTThreadClient(self.name,self.queue_mc_send,self.queue_mc_recv)
        self.dvcs.update({
            'sro1':sro1,'sro2':sro2,
            'cam1':cam1,'cam2':cam2})

        self._sys_write=sys.stdout.write
        sys.stdout.write=self.writeOut
        return

    def METMain(self):
        self.client.startClient()
        while not self.FLAG_EXIT:
            if len(self.queue_mc_recv)!=0:
                try:
                    self.processRecv(self.queue_mc_recv.pop(0))
                except BaseException as e:c.bug(e)

            time.sleep(0.1)
        self.exitMET()
        return

    def processRecv(self,data):
        met=self
        i=data.find('://')
        if i!=-1:
            head=data[0:i]
            body=data[i+3:]
            if head=='MTCMD':
                i_self=body.find('self')
                if i_self!=-1:
                    try:exec(body)
                    except BaseException as e:c.bug(e)
                else:
                    i_dot=body.find('.')
                    name=body[0:i_dot]
                    try:exec('self.dvcs["'+name+'"]'+body[i_dot:])
                    except BaseException as e:c.bug(e)
        return

    def writeOut(self,string):
        string=string.strip()
        if len(string)>2:
            self._sys_write(self.header+string+'\n')
            sys.stdout.flush()
        return

    def exitMET(self):
        for dvc in self.dvcs.values():
            dvc.close()
        return exit()
    pass
