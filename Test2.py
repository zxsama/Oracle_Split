import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# source = cv2.imread("D:/Users/84460/Desktop/Oracle_Split/picture/003.png",0)          # 读图片
def file_name(dir_path):
    f_name = []
    f_namelist = []
    print(os.listdir(dir_path))
    
    for i in f_namelist:#分割后缀
        index = i.rfind('.')
        f_name.append(i[:index])
    return f_name,f_namelist

save_path = "D:/Users/84460/Desktop/Oracle_Split/picture/"
f_name, f_namelist = file_name(save_path)

image_len = len(f_name)

peek_ranges = [(17, 53), (67, 98), (113, 144), (160, 191), (210, 216), (229, 236), (256, 262), (276, 282),(302,322)] 

#对文字分割进行整理，去除上下结构分割错误

a_len = 10 #两字间距
a_len_e = 15 #例如“ 一二 ”的两字间距更大一点
b_len = 18 #单字高度最低限

#合并上下结构文字
peek_ranges_new = []
peek_ranges = np.array(peek_ranges)
peek_ranges = peek_ranges.flatten()
peek_ranges_new.append(peek_ranges[0])
flag=0
for i in range(1,len(peek_ranges) - 1):
    if(flag==0):   
        if(peek_ranges[i+1] - peek_ranges[i] > a_len):
            peek_ranges_new.append(peek_ranges[i])
            peek_ranges_new.append(peek_ranges[i+1])
        flag = 1
    else:
        flag -= 1
peek_ranges_new.append(peek_ranges[len(peek_ranges)-1])

#合并 “二”
peek_ranges_new1 = []
flag=0
end_flag=0
end_temp=0
for i in range(len(peek_ranges_new)):
    print("i:", i,"\t",len(peek_ranges_new),"  ",peek_ranges_new[i])
    if(flag==0): 
        if(peek_ranges_new[i+1] - peek_ranges_new[i] > b_len):#判断是否是结构件（包括 “一” ） （>：否， <：是）
            if(end_flag == 1):#标志位判断上一个是否是结构件，识别类似结构件高度的文字 （例如“一”）
                print("111","\t" ,i ,"\t",peek_ranges_new[i],"\t",end_temp)
                end_flag = 0
                end_temp = peek_ranges_new[i - 1]
                peek_ranges_new1.append(end_temp)
            print("222","\t" ,i ,"\t",peek_ranges_new[i],"\t",end_temp)
            peek_ranges_new1.append(peek_ranges_new[i])
            peek_ranges_new1.append(peek_ranges_new[i+1])
        else:
            if(end_flag == 0): #识别两个以上结构件
                print("333","\t" ,i ,"\t",peek_ranges_new[i],"\t",end_temp)
                end_flag = 1
                peek_ranges_new1.append(peek_ranges_new[i])
                end_temp = peek_ranges_new[i+1]
  
            elif(end_flag == 1 and peek_ranges_new[i] - peek_ranges_new[i-1] < b_len): #判断间距，两个结构件
                print("444","\t" ,i ,"\t",peek_ranges_new[i],"\t",end_temp)
                end_temp = peek_ranges_new[i+1]

            elif(end_flag == 1 and peek_ranges_new[i] - peek_ranges_new[i-1] >= a_len_e): #判断间距，两个文字
                print("555","\t" ,i ,"\t",peek_ranges_new[i],"\t",end_temp)
                peek_ranges_new1.append(end_temp)
                end_flag = 0

                peek_ranges_new1.append(peek_ranges_new[i])
                end_temp = peek_ranges_new[i+1]   
                end_flag = 1

            if(end_flag == 1 and i==(len(peek_ranges_new)-2)):
                print("666","\t" ,i ,"\t",peek_ranges_new[i],"\t",end_temp)
                peek_ranges_new1.append(end_temp) 
        flag = 1
    else:
        flag -=1

print(end_temp)
print(peek_ranges_new,type(peek_ranges_new))
print(peek_ranges_new1,type(peek_ranges_new1))