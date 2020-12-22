import sys
import cv2
import urllib.request as url
import numpy as np
import core as c
host = c.pi_host+':'
if len(sys.argv)>1:
    host = sys.argv[1]
hoststr = 'http://' + host + '/?action=stream'
print('Streaming ' + hoststr)

print('Print Esc to quit')
stream=url.urlopen(hoststr)
bytes=''
while True:
    bytes+=stream.read(1024)
    a = bytes.find('\xff\xd8')
    b = bytes.find('\xff\xd9')
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        # flags = 1 for color image
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),flags=1)
        # print i.shape
        cv2.imshow("xiaorun",i)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(0)
