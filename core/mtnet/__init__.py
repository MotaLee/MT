import sys,time,socket,select,threading
import multiprocessing as mp
from multiprocessing.queues import Queue
import nmap
import core as c

# define host ip: Rpi's IP
def getLocalIp():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip = s.getsockname()[0]
    finally: s.close()
    return str(ip)

def getDeviceHost(name,localhost='',mac=''):
    # 'todo: optimize'
    # if name=='RaspberryPi':
    #     host='192.168.2.111'
    # else:
    #     host=c.INDEX['MTServers']['MCT']['host']
    if localhost=='':localhost=getLocalIp()
    prefix=localhost[0:localhost.rfind('.')]
    scanner=nmap.PortScanner()
    scanner.scan(prefix+'.100-200')
    all_host=scanner.all_hosts()

    host=''
    for host in all_host:
        hn=scanner[host]['hostnames']
        hn=hn[0]['name']
        if hn.lower().find(name.lower()):
            host=host
            break
    return host

class ProcessQueue(Queue):
    def __init__(self):
        super().__init__(ctx=mp.get_context())
        return
    pass

class MTProcessServer(mp.Process):
    def __init__(self,sn,que_stdout,que_send,que_recv,ip="local",port=8888,report=False):
        super().__init__(target=self.runServer,args=(que_stdout,que_send,que_recv),daemon=True)
        if ip=='local':ip=getLocalIp()
        self.IP=ip
        self.PORT=port
        self.socket_con=None
        self.sock =None
        self.queue_stdout=que_stdout
        self.queue_send=que_send
        self.queue_recv=que_recv
        self.header='[MTServer '+sn+']'
        self.FLAG_EXIT=False
        return

    def startServer(self,run=True):
        c.info('Start MTServer...',level=self.header+'Info')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 不经过WAIT_TIME，直接关闭
        self.sock.setblocking(False)                                     # 设置非阻塞编程
        c.info('TCP server listen @ '+str(self.IP)+':'+str(self.PORT),level=self.header+'Info')
        host_addr = (self.IP, self.PORT)
        self.sock.bind(host_addr)
        self.sock.listen(1)
        if run:self.start()
        return self.socket_con

    def runServer(self,que_stdout,que_send,que_recv):
        sys.stdout.write=que_stdout.put
        inputs =[self.sock]
        while not self.FLAG_EXIT:
            r_list,w_list,e_list=select.select(inputs,list(),list(), 1)
            for event in r_list:
                if event == self.sock:
                    c.info("New client connection.",level=self.header+'Info')
                    new_sock,addr=event.accept()
                    inputs.append(new_sock)
                else:
                    try:
                        data = event.recv(512)
                        que_recv.put(data.decode())
                    except BaseException:
                        c.info("Client disconnected.",level=self.header+'Info')
                        inputs.remove(event)
                        self.FLAG_EXIT=True
            for sock in inputs:
                if sock!=self.sock:
                    try:
                        datain=que_send.get(timeout=0.1)
                        sock.send(datain.encode())
                        sendlen=str(len(datain))
                        c.info("Sent Message: "+sendlen,level=self.header+'Info')
                    except BaseException:pass

            time.sleep(0.5)
        return exit()

    def send(self,data,header='MTCMD'):
        if header is not None:
            self.queue_send.put(header+'://'+data)
        else:self.queue_send.put(data)
        return
    pass

class MTThreadClient(threading.Thread):
    def __init__(self,sn,que_send,que_recv):
        super().__init__(name=sn,target=self.runClient)
        self.queue_send=que_send
        self.queue_recv=que_recv
        self.ip =c.INDEX['MTServers']['MCT']['host']
        self.port = 8888
        self.sock=None
        # self.header='[MTClient '+sn+']: '
        self.header=''
        return

    def startClient(self,run=True):
        c.info(self.header+"Starting socket: TCP...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)

        cntres=self.cntClient()

        if run and cntres:self.start()
        elif not cntres:c.info(self.header+'Connection failed.')
        return

    def cntClient(self):
        retry=10
        server_addr = (self.ip,self.port)
        if sys.platform.find('win')!=-1:normal_err=WindowsError
        else:normal_err=IOError
        while retry>0:
            try:
                c.info(self.header+"Connecting to server @ "+self.ip+':'+str(self.port))
                self.sock.connect(server_addr)
                break
            except normal_err as e:
                print(e)
                break
            except BaseException as e:
                print(e)
                c.bug(self.header+"Can't connect to server,will try it in 5s.")
                retry-=1
                time.sleep(5)
                continue
        if retry==0:return False
        else: return True
        return

    def runClient(self):
        r_inputs ={self.sock}
        w_inputs ={self.sock}
        e_inputs ={self.sock}
        while True:
            try:
                r_list,w_list,e_list=select.select(r_inputs, w_inputs, e_inputs, 1)
                for event in r_list:
                    # print("r")              # 产生了可读事件，即服务端发送信息
                    try:data = event.recv(1024)
                    except Exception as e:
                        c.bug(e)
                        continue
                    if data:
                        c.info(self.header+"Data received "+ str(len(data)))
                        self.queue_recv.append(data.decode())
                    else:
                        c.info(self.header+"Disconnected.")
                        r_inputs.clear()
                if len(w_list) > 0:     # 产生了可写的事件，即连接完成
                    c.info('Connecting succeed.')
                    w_inputs.clear()    # 当连接完成之后，清除掉完成连接的socket
                if len(e_list) > 0:  # 产生了错误的事件，即连接错误
                    c.bug('Connecting err.')
                    e_inputs.clear()    # 当连接有错误发生时，清除掉发生错误的socket
                if len(self.queue_send)!=0:
                    self.sock.send(self.queue_send.pop(0).encode())
                # time.sleep(0.5)
            except BaseException as e:
                c.bug(e)
                if str(e).find('32')!=-1:
                    self.queue_recv.append('MTCMD://self.FLAG_EXIT=True')
                    break
        return
    pass
