import sys,threading

import wx
import core as c
from core import mtnet
# App variable;
MCT_VER='0.0.1'
MCT_TITLE='MindTank Control Terminal'
WXAPP=wx.App(redirect=True,filename=None)
cx,cy,cw,ch=wx.ClientDisplayRect()
xu=cw/100
yu=ch/100

class MCT(object):
    def __init__(self,intergrated=False):
        self.ms=None
        self.FLAG_MCT_EXIT=False
        self.FLAG_INTERGRATED=intergrated
        self.queue_input=list()
        self.queue_ms_send=mtnet.ProcessQueue()
        self.queue_ms_recv=mtnet.ProcessQueue()
        self.queue_ms_stdout=mtnet.ProcessQueue()
        return

    @staticmethod
    def clear():
        ''' For rebinding.'''
        return

    def terminalMain(self):
        print('MindTank Control Terminal '+MCT_VER)
        # if self.main_server:
        if self.FLAG_INTERGRATED:
            while not self.FLAG_MCT_EXIT:
                if len(self.queue_input)>0:
                    try:self.processCmd(self.queue_input.pop(0))
                    except BaseException as e:c.bug(e)
                try:
                    ms_recv=self.queue_ms_out.get(timeout=0.1)
                    if ms_recv:print(ms_recv)
                    self.processRecv(ms_recv)
                except BaseException:pass
                try:
                    ms_stdout=self.queue_ms_stdout.get(timeout=0.1)
                    if ms_stdout:print(ms_stdout)
                except BaseException:pass
        else:
            pass
            # self.ms=mtnet.MTThreadServer('ms',
            #     self.queue_msin,self.queue_msout,report=True)
            # self.ms.startServer()
            # while not self.FLAG_MCT_EXIT:
            #     cmd= input('MCT>>')
            #     try:exec(cmd)
            #     except BaseException as e:c.bug(e)
        exit()

    def processCmd(self,cmd):
        mct=self
        try:exec(cmd)
        except NameError:
            try:exec('self.'+cmd)
            except BaseException as e:c.bug(e)
        return cmd

    def processRecv(self,recv):
        recv=recv.decode()
        i=recv.find('://')
        if i!=-1:
            head=recv[0:i]
            body=recv[i+3:]
            # if head=='MTCMD':exec(body)
        return

    pass

class MTMFont(wx.Font):
    ''' Simple font class.

        Para argkw: size.'''
    def __init__(self,**argkw):
        size=argkw.get('size',12)
        TEXT_FONT=argkw.get('font','Microsoft YaHei')
        super().__init__(int(size),wx.MODERN,wx.NORMAL,wx.NORMAL,False,TEXT_FONT)
    pass

# Editor main window;
class MCTX(wx.Frame):
    def __init__(self):
        super().__init__(None,pos=(cx,cy),size=(cw,ch),title=MCT_TITLE+' '+MCT_VER,
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.MAXIMIZE)

        self.terminal=MCT(intergrated=True)
        self.server=mtnet.MTProcessServer('ms',self.terminal.queue_ms_stdout,
            self.terminal.queue_ms_send,self.terminal.queue_ms_recv,report=True,port=8888)
        self.terminal.ms=self.server
        self.thread_mct=threading.Thread(target=self.terminal.terminalMain,daemon=True)
        self.thread_met=threading.Thread(target=self.detectMET,daemon=True)

        self.font_select=MTMFont(size=2*yu-2)
        self.font_txt=MTMFont(size=yu)

        self.btn_lnch=wx.Button(self,pos=(int(yu),int(yu)),
            size=(int(8*yu),int(4*yu)),label='▶启动')
        self.slt_lnch=wx.ComboBox(self,pos=(int(10*yu),int(yu)),
            size=(int(24*yu),int(4*yu)),choices=['0.MET:U/L','1.MET:L'])
        self.slt_lnch.SetFont(self.font_select)
        self.slt_lnch.Select(0)

        self.lbl_mctx=wx.StaticText(self,pos=(int(yu),int(6*yu)),
            size=(int(8*yu),int(4*yu)),label='MCTX:')
        self.txt_in=wx.TextCtrl(self,pos=(int(10*yu),int(6*yu)),
            size=(int(65*xu-16*yu),int(4*yu)),style=wx.TE_PROCESS_ENTER)
        self.btn_input=wx.Button(self,pos=(int(65*xu-5*yu),int(6*yu)),
            size=(int(4*yu),int(4*yu)),label='▷')
        self.txt_out=wx.TextCtrl(self,pos=(int(yu),int(11*yu)),
            size=(int(65*xu-2*yu),int(84*yu)),style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.lbl_mctx.SetFont(self.font_select)
        self.txt_in.SetFont(self.font_select)
        self.txt_out.SetFont(self.font_select)

        self.lbl_ms=wx.StaticText(self,pos=(int(65*xu),int(yu)),
            size=(int(35*xu-yu),int(4*yu)),label='Main server:')
        self.txt_ms=wx.TextCtrl(self,pos=(int(65*xu),int(6*yu)),
            size=(int(35*xu-yu),int(41*yu)),style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.lbl_mc=wx.StaticText(self,pos=(int(65*xu),int(48*yu)),
            size=(int(35*xu-yu),int(4*yu)),label='Client:')
        self.txt_mc=wx.TextCtrl(self,pos=(int(65*xu),int(54*yu)),
            size=(int(35*xu-yu),int(41*yu)),style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.txt_in.Bind(wx.EVT_TEXT_ENTER,self.onEnterCmd)
        self.btn_lnch.Bind(wx.EVT_LEFT_DOWN,self.onClkLaunch)

        self.Show()
        sys.stdout.write=self.writeOut
        self.terminal.clear=self.txt_out.Clear
        self.thread_mct.start()
        self.server.startServer()
        return

    def onEnterCmd(self,e):
        cmd=self.txt_in.Value
        self.txt_in.Clear()
        print('[MCTX]: '+cmd)
        self.terminal.queue_input.append(cmd)
        return

    def onClkLaunch(self,e):
        ssh=c.findPi()
        if ssh is None:return
        item=int(self.slt_lnch.Value[0])
        if item==0:
            c.updatePi(ssh,True)
            self.chan_client=c.runMET(ssh)
            self.thread_met.start()
        elif item==1:
            self.chan_client=c.runMET(ssh)
            self.thread_met.start()
        return

    def writeOut(self,string):
        string=string.strip('\n')
        if string:
            if string.find('[MTServer')!=-1:
                self.txt_ms.AppendText(string+'\n')
            elif string.find('[MET')!=-1:
                self.txt_mc.AppendText(string+'\n')
            else:
                self.txt_out.AppendText(string+'\n')
        return

    def detectMET(self):
        while not self.chan_client.closed:
            data=self.chan_client.recv(512).decode()
            lines=data.splitlines(keepends=False)
            for line in lines:
                if line.find('[MET')!=-1:print(line)
        return
    pass
