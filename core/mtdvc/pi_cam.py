import fcntl,ctypes,time,subprocess,os
import v4l2
from . import MTPiDvc
CAMERA_DEVICE="/dev/video0"
INITIAL_IMAGE_PATH="/home/Photos/"
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_FORMAT=v4l2.V4L2_PIX_FMT_JPEG
BUFFER_COUNT=2    # image count in device buffer queue
DESIRED_IMAGE_COUNT=5

class VideoBuffer(ctypes.Structure):
    _field_=[
        ('start',ctypes.c_void_p),
        ('length',ctypes.c_size_t)]
    pass

# get each image's path name via different catching time
def getImgName(string,num):
    date=time.strftime('%Y%M%D-%H%M%S')
    return str(string+num+date)

def main():
    fd=0    # camera handle
    image_path=INITIAL_IMAGE_PATH

    #  open file of camera
    print("#open camera:\n")
    fd=open(CAMERA_DEVICE,v4l2.O_RDWR,0)
    if fd == -1:
        print("failed to open camera!\n")
        exit()
    print("fd=%d\n",fd)

    # query driver's capability
    print("\n#query driver's capability:\n")
    cap=v4l2.v4l2_capability()
    if(fcntl.ioctl(fd,v4l2.VIDIOC_QUERYCAP,cap)== -1):
        print("failed to query driver's driver capability!\n")
        exit(0)
    print("cap.capabilities=0x%x\n",cap.capabilities)

    # enumerate image format(s) driver supported
    print("\n#enumerate image format(s) driver supported:\n")
    fmtdesc=v4l2.v4l2_fmtdesc()
    fmtdesc.index=0
    fmtdesc.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    print("image format(s) driver supported:\n")
    ioctl_error=0
    while ioctl_error==0:
        ioctl_error=fcntl.ioctl(fd,v4l2.VIDIOC_ENUM_FMT,fmtdesc)
        print("index:%d,flag:%d, format name:%s,pixelformat=0x%x \n",
            fmtdesc.index,fmtdesc.flags,fmtdesc.description,fmtdesc.pixelformat)
        fmtdesc.index+=1

    # set frame format
    print("\n#set frame format:\n")
    format=v4l2.v4l2_format()
    # memset(&format,0,sizeof(struct v4l2_format))
    format.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    format.fmt.pix.width = VIDEO_WIDTH  # width of frame photo
    format.fmt.pix.height = VIDEO_HEIGHT  # hight of frame photo
    format.fmt.pix.pixelformat=VIDEO_FORMAT  # frame format
    ioctl_error=fcntl.ioctl(fd, v4l2.VIDIOC_TRY_FMT,format)
    print("ioctl_errorurn value of VIDIOC_TRY_FMT=%d\n",ioctl_error)
    ioctl_error=fcntl.ioctl(fd, v4l2.VIDIOC_S_FMT,format)
    print("ioctl_errorurn value of VIDIOC_S_FMT=%d\n",ioctl_error)

    #  Release the resource
    # for (numBufs=0 numBufs< req.count numBufs++)
    # {
    #     munmap(video_buf[numBufs].start, video_buf[numBufs].length)
    # }

    # close file of camera
    print("\n#close camera:\n")
    if fd!=-1:
        if(fd.closed!= -1):print("succeed to close camera!\n")
    else:
        print("failed to close camera!\n")
        exit()

    # free memory
    # free(Video_buf)

    return

def recordVideo(fd):
    # apply memory for images from catching video
    print("\n#apply memory for images from catching video:\n")
    req=v4l2.v4l2_requestbuffers  # buffer in device
    req.count =BUFFER_COUNT
    req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    req.memory =v4l2.V4L2_MEMORY_MMAP
    if fcntl.ioctl(fd,v4l2.VIDIOC_REQBUFS,req) == -1:
        # VIDIOC_REQBUFS means allocate memory from device
        print("failed to apply memory for images from catching video!\n")
        exit()

    # apply phycisal(program) memory and map it to memory of images
    print("\n#apply phycisal memory and map it to memory of images:\n")
    video_buf=list()*req.count
    video_buf=VideoBuffer()
    # VideoBuffer* video_buf = calloc(req.count, sizeof(*video_buf))
    buf=v4l2.v4l2_buffer()
    numBufs=0
    for i in range(req.count):
        # memset( &buf, 0, sizeof(buf) )
        buf.index = numBufs
        buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = v4l2.V4L2_MEMORY_MMAP

        # apply buffer memory from device
        if fcntl.ioctl(fd, v4l2.VIDIOC_QUERYBUF,buf) == -1:
            print("faild to get buffer memory%d\n",numBufs)
            exit()

        # video_buf[numBufs].length = buf.length
        #  map device buffer into program memory so that we can get information of image(s) and display in monitor
        # video_buf[numBufs].start = mmap(None, buf.length, PROT_READ | PROT_WRITE,MAP_SHARED,fd, buf.m.offset)
        # if (video_buf[numBufs].start == MAP_FAILED)
        # {
        #     print("video_buf[%d] ",numBufs)
        #     perror("map error:")
        #     exit(0)
        # }

        # queue buffer to save images from device
        if fcntl.ioctl(fd,v4l2.VIDIOC_QBUF, buf) == -1:
            print("fiald to push into buffer queue\n")
            exit()
        # print("Frame buffer %d: address=0x%x, length=%d\n",
            # numBufs, (unsigned int)video_buf[numBufs].start, video_buf[numBufs].length)

    # start to record video
    print("\n#start to record video:\n")
    enumtype=v4l2.v4l2_buf_type
    # enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE
    ioctl_error =fcntl.ioctl(fd, v4l2.VIDIOC_STREAMON, enumtype)
    # VIDIOC_STREAMON： start command:video captuer,then  the device program will start
    # colloct video data and save it into device's buffer
    if ioctl_error < 0:
        print("VIDIOC_STREAMON failed (%d)\n", ioctl_error)
        exit()

    for loop_i in range(DESIRED_IMAGE_COUNT):
        #  Get frame
        ioctl_error = fcntl.ioctl(fd, v4l2.VIDIOC_DQBUF, buf)
        # get a photo from device and save into device buffer,because of mapping before,
        # it also saved into program memory
        if ioctl_error < 0:
            print("VIDIOC_DQBUF failed (%d)\n", ioctl_error)
            exit()

        #  save frame
        image_path=str(INITIAL_IMAGE_PATH)
        # Re-initialise path name of image
        # get_image_name(image_path,loop_i+1)# get new path name

        fp = open(image_path, "wb")
        if fp < 0:
            print("open frame data file failed\n")
            exit()
        fp.write(video_buf)
        # fwrite(video_buf[buf.index].start, 1, buf.length, fp)
        fp.close()
        print("Capture frame%d saved in %s\n",loop_i+1,image_path)

        #  Re-queen buffer
        ioctl_error =fcntl.ioctl(fd, v4l2.VIDIOC_QBUF,buf)
        if ioctl_error < 0:
            print("VIDIOC_QBUF failed (%d)\n", ioctl_error)
            exit()

    return

class PiMjpgCam(MTPiDvc):
    def __init__(self,**argkw):
        super().__init__(argkw)
        self.addr=argkw.get('addr',0)
        self.port=str(argkw.get('port',8080))
        cmd='./res/lib/mjpg-streamer -i "input_uvc.so -d '+\
            '/dev/video'+str(self.addr)+\
            '" -o "output_http.so -p '+self.port+'"'
        self.pipe=subprocess.Popen(cmd,shell=False,cwd=os.getcwd())
        return

    def close(self):
        self.pipe.kill()
        return
    pass
