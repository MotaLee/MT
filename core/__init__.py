import sys,os,json,tarfile,time
import paramiko
sys.path.append(os.getcwd())
from core import mtnet
fd_mtindex=open(os.getcwd()+'/mem/index.json','r')
INDEX=json.load(fd_mtindex)
LOG=list()
MT_POOL=dict()
MT_NMAX=1

tar_path="/home/pi/Project/MT"
pi_user='pi'
pi_hostname='RaspberryPi'
pi_name='Lan'
pi_pwd=INDEX['MTClients'][pi_name]['pi_pwd']
pi_host=str(INDEX['MTClients'][pi_name]['pi_host'])
pi_port=22


class MTData(object):
    def __init__(self,name):
        self.ssh=None
        self.name=name
        index_dict=INDEX['MTClients'][name]
        self.mtid=index_dict['mtid']
        self.pi_host=index_dict['pi_host']
        self.pi_user=index_dict['pi_user']
        self.pi_pwd=index_dict['pi_pwd']
        return
    pass

def info(string,level='Info',report=False):
    string=level+': '+str(string)
    LOG.append(time.strftime('%Y%M%D-%H%M%S')+': '+string)
    print(string)
    # if report:
    # else:raise BaseException(string)
    return string

def bug(string):
    info(string,level='Err')
    return string

def makeTargz(outname, srcdir,subdir=None):
    if subdir is None:subdir=['']
    try:
        with tarfile.open(outname, "w") as tar:
            for sub in subdir:
                tar.add(srcdir+sub, arcname=os.path.basename(srcdir+sub))
        return True
    except Exception as e:
        print(e)
        return False
    return

def saveIndexJson():
    with open(os.getcwd()+'/mem/index.json','w') as fd_mtindex:
        json.dump(INDEX,fd_mtindex)
    return

def updatePi(ssh=None,keepssh=False):
    tar_name='_mt.tar.gz'
    tar_files=['\\app','\\core','\\mem','\\MT.py']
    try:
        info('Updating MT.')
        makeTargz(tar_name,os.getcwd(),tar_files)
        trans = paramiko.Transport(sock=(pi_host,22))
        trans.connect(username=pi_user,password=pi_pwd)
        sftp = paramiko.SFTPClient.from_transport(trans)
        sftp.put(tar_name,tar_path+'/'+tar_name)
        sftp.close()
        os.remove(tar_name)
        info('Tar uploaded to MT.')

        info('Unzipping tar in MT.')
        ssh=getSSH()
        command='cd '+tar_path+';tar -xvf '+tar_name
        stdin,stdout,stderr=ssh.exec_command(command,get_pty=True)
        command='cd '+tar_path+';rm '+tar_name
        ssh.exec_command(command,get_pty=True)
        info('Tar in MT unzipped.')
        if keepssh:return ssh
        else:ssh.close()
    except BaseException:pass
    return

def runMET(ssh=None):
    info('Launching MET.')
    cmd='cd '+tar_path+';'
    cmd+='python3 MT.py MET\n'
    if ssh is None:ssh=getSSH()
    channel=ssh.invoke_shell()
    channel.send(cmd)
    info('MET Launched.')
    return channel

def getSSH(**argkw):
    ''' Return None if connecting failed.'''
    host=argkw.get('host',pi_host)
    port=argkw.get('port',pi_port)
    user=argkw.get('port',pi_user)
    pwd=argkw.get('port',pi_pwd)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host, port=port,
            username=user, password=pwd,timeout=5.0)
    except BaseException:return None
    return ssh

def findPi(mtname='Lan',port=8888):
    global INDEX
    mct=INDEX['MTServers']['MCT']
    met=INDEX['MTClients'][mtname]
    localhost=mtnet.getLocalIp()
    localport=port
    pi_host=met['pi_host']
    ssh=getSSH()
    if ssh is None:
        pi_name=met['pi_name']
        pi_host=mtnet.getDeviceHost(pi_name)
        if pi_host is None:
            bug('Pi not found.')
            return None
        else:
            ssh=getSSH(host=pi_host)
            met['pi_host']=pi_host
    # pi_port=met['pi_port']
    mct['host']=localhost
    mct['port']=localport
    met['pi_port']=localport
    saveIndexJson()
    return ssh
