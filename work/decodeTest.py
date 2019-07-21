s = '\xe5\x86\x96\xe7\x8e\x8b\xe5\xa4\xa7\xe4\xbb\xa4\xe6\x9e\xad\xe4\xba\xba\xe6\x9b\xb0\xe6\x9a\x82\xe5\x86\x96\xe7\x94\xb0\xe5\x85\xb6\xe5\x8f\x97\xe5\xb9\xb4\xe5\x86\x96\xe5\x8d\x81\xe4\xb8\x80'
sss = s.encode('raw_unicode_escape').decode()
print(sss)
""" import base64
import cv2
import numpy as np
import PIL.Image 
import matplotlib.pyplot
import pdb

filepath = "D:/Users/84460/Desktop/Oracle_Split/outpic/01/a/"
filename="m_01_0003_a_6_6.jpg"

image = cv2.imread(filepath + filename)
print(image)
            
f = open(image, 'rb')  # 二进制方式打开图文件

# 参数image：图像base64编码
img = base64.b64encode(f.read())

print(f.read())

#print(image.tobytes())
x=image.tobytes()
im = cv2.imdecode(np.fromstring(x, np.uint8),1)
print(im) """