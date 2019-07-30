#main.py
import os
import cv2
import time
import gc
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(r'./')
import typeimg_strict as ti

# 区域分割预处理
def imgDeal(img):
    #new_shape = (image_color.shape[1], image_color.shape[0])
    #image = cv2.resize(image_color, new_shape)
    image_cvt = cv2.cvtColor(image_sour, cv2.COLOR_BGR2GRAY)# 灰度化
    image_blurred = cv2.GaussianBlur(image_cvt,(5, 5),0) # 高斯模糊，过滤文本杂边
    image_bil = cv2.bilateralFilter(image_blurred, 9, 25, 10)# 双边滤波,用于除去脏迹
    image_median = cv2.medianBlur(image_bil,9)# 中值滤波   
    image_adap = cv2.adaptiveThreshold(# 自适应阈值二值化 adaptive_threshold
        image_median,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
        cv2.THRESH_BINARY, 11, 10)  
    image_canny = cv2.Canny(image_adap, 100, 400, 5)

    _,RedThresh = cv2.threshold(image_canny,160,255,cv2.THRESH_BINARY)#膨胀图像,便于直线检测画边界
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(8, 8))
    image_dilated = cv2.dilate(RedThresh,kernel) 
    return image_dilated

# 文字分割预处理
def imgDeal_type(img):

    _, image_thres=cv2.threshold(img,220,255,cv2.THRESH_TRUNC)# 阈值分割

    image_cvt = cv2.cvtColor(image_thres, cv2.COLOR_BGR2GRAY)# 灰度化

    kernel_oc = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))#开闭
    dst_OPEN = cv2.morphologyEx(image_cvt, cv2.MORPH_OPEN, kernel_oc)
    dst_CLOSE = cv2.morphologyEx(dst_OPEN, cv2.MORPH_CLOSE, kernel_oc)  

    image_blurred = cv2.GaussianBlur(dst_CLOSE,(5, 5),0) # 高斯模糊，过滤文本杂边 
    image_adap = cv2.adaptiveThreshold(# 自适应阈值二值化 adaptive_threshold
        image_blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
        cv2.THRESH_BINARY_INV, 5, 4)  

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(4, 4))
    _,RedThresh = cv2.threshold(image_adap,160,255,cv2.THRESH_BINARY)#膨胀图像,便于直线检测画边界
    image_dilated = cv2.dilate(RedThresh,kernel) 
    return image_dilated

# 直线检测
def imgLines(img):
    image_lines = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # HoughLinesP函数是概率直线检测，注意区分HoughLines函数
    lines = cv2.HoughLinesP(img, 1, np.pi/180, 60, 1500, 1500)

    for i in range(0, len(lines)):     # line 函数勾画直线
        for x1,y1,x2,y2 in lines[i]:   # (x1,y1),(x2,y2)坐标位置
            cv2.line(image_lines, (x1,y1), (x2,y2), (0,0,255), 8)

    #print("lines:",len(lines))
    return image_lines

# 轮廓检测
def imgContours(img):
    img8 = img
    img8 = cv2.convertScaleAbs(img, img8, 1, 0); # 转换输入数组元素成8位无符号整型
    #image_Con = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    #opencv4中findContours输出两个值
    (cnts, _) = cv2.findContours(img8, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE)
    c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

    # compute the rotated bounding box of the largest contour
    rect = cv2.minAreaRect(c) #生成最小外接矩形
    box = np.int0(cv2.boxPoints(rect))
    #print("box", box)
    # 绘制矩形
    draw_img = cv2.drawContours(image_sour.copy(), [box], -1, (0, 255, 0), 4)
    return draw_img, box

# 透视变换
def imgPerspective(img, corners):
    canvas=[[0, 0], [2156, 0], [0, 3172], [2156, 3172]]

    pointsort = np.array([0, 0, 0, 0])#对矩形对应的点进行排序
    for i in range(4):
        pointsort[i] = sum(corners[i])
    sort_index = np.argsort(pointsort)
    corners_sort = corners[sort_index]
    
    canvas = np.float32(canvas)# getPerspectiveTransform只接收float32类型的数据
    corners_sort =  np.float32(corners_sort)
    M = cv2.getPerspectiveTransform(corners_sort, canvas)
    image_result = cv2.warpPerspective(img, M, (2156, 3172))

    #print(pointsort,type(pointsort))
    #print(corners,type(corners))
    #print(corners_sort,type(corners_sort))
    #print(canvas,type(canvas))
    #print(M,type(M))
    return image_result

# 修饰并绝对分割
def imgSplit(img):
    img = cv2.rectangle(img, (0, 1800), (3172, 1860), (255, 255, 255), -1)
    # img_temp = np.zeros((60, 3172, 3), np.uint8)
    # img_temp.fill(255)
    #
    # img[1800:1860,00:3172] = img_temp
    cropped = img[15:3157, 15:2141]
    imsplit_a = cropped[0:390,:]
    imsplit_b = cropped[450:1800,:]
    imsplit_c = cropped[1860:3150,:]
    imsplit_bc= cropped[450:3150,:]
    #plt.imshow(img)
    #plt.show()
    return cropped, imsplit_a, imsplit_b, imsplit_c, imsplit_bc

#获取文件名
def file_name(dir_path):
    global f_name
    global f_namelist#文件或文件夹名称（图片）

    f_name = []
    f_namelist = []

    for files in os.listdir(dir_path):
        f_namelist.append(files)

    for i in f_namelist:#分割后缀
        index = i.rfind('.')
        f_name.append(i[:index])
    return f_name,f_namelist

if __name__ == "__main__":

    R_dir_path = "D:/Users/84460/Desktop/Oracle_Split/Picture/"
    R_save_path = "D:/Users/84460/Desktop/Oracle_Split/outpic_strict/"
    f_name, f_pathlist = file_name(R_dir_path)

    time_all=0

    for essaycounts in range(len(f_pathlist)):
        dir_path = R_dir_path + f_pathlist[essaycounts] + "/"
        save_path = R_save_path + f_pathlist[essaycounts] + "/"

        f_name, f_namelist = file_name(dir_path)

        image_len = len(f_name)
        
        #image_len=1
        # imcont=1

        for imcounts in range(image_len):
            time_start=time.time()
            print("path: "+dir_path + f_namelist[imcounts])

            image_sour = cv2.imread(dir_path + f_namelist[imcounts], cv2.IMREAD_COLOR) #读文件
            # image_sour = cv2.imread("D:/Users/84460/Desktop/Oracle_Split/work/063.png", cv2.IMREAD_COLOR)         
            image_deal = imgDeal(image_sour)# 预处理
            image_lines = imgLines(image_deal)# 直线检测
            draw_img, box = imgContours(image_deal)# 轮廓检测
            image_result = imgPerspective(image_sour, box)# 透视变换
            cropped, imsplit_a, imsplit_b, imsplit_c, imsplit_bc= imgSplit(image_result)# 修饰并区域分割

            #imsplit_a_deal = imgDeal_type(imsplit_a)# 预处理
            #imsplit_b_deal = imgDeal_type(imsplit_b)
            imsplit_bc_deal = imgDeal_type(imsplit_bc)

            #plt.imshow(imsplit_bc_deal)
            #plt.show()

            horizontal_sum = ti.verticalSplit(imsplit_bc_deal)# a文字分割
            peek_ranges = ti.extract_peek_ranges_from_array(horizontal_sum)
            vertical_peek_ranges, vertical_peek_ranges2d = ti.extract_peek_source(peek_ranges, imsplit_bc_deal)# 列
            vertical_peek_ranges2d, peek_ranges = ti.deal_vertical_peek_ranges2d(vertical_peek_ranges2d, peek_ranges)
            new_img_B = ti.imageCompose(peek_ranges,imsplit_b,1350) #b列
            new_img_C = ti.imageCompose(peek_ranges,imsplit_c,1296) #C列
            #print(peek_ranges)
            #print(vertical_peek_ranges2d)
            ti.imgEachType(peek_ranges, vertical_peek_ranges2d, imsplit_bc, save_path, f_name[imcounts],'b','c', new_img_B, new_img_C)# 行，并保存


            
            '''
            horizontal_sum = ti.verticalSplit(imsplit_a_deal)# a文字分割
            peek_ranges = ti.extract_peek_ranges_from_array(horizontal_sum)
            #peek_ranges_clear = ti.Clear_peekrangesclear(peek_ranges)
            vertical_peek_ranges, vertical_peek_ranges2d = ti.extract_peek_source(peek_ranges, imsplit_a_deal)# 列
            ti.imgEachType(peek_ranges, vertical_peek_ranges2d, imsplit_a, save_path, f_name[imcounts],'a')# 行，并保存

            horizontal_sum = ti.verticalSplit(imsplit_b_deal)# b文字分割
            peek_ranges = ti.extract_peek_ranges_from_array(horizontal_sum)
            #peek_ranges_clear = ti.Clear_peekrangesclear(peek_ranges)
            vertical_peek_ranges, vertical_peek_ranges2d = ti.extract_peek_source(peek_ranges, imsplit_b_deal)# 列
            ti.imgEachType(peek_ranges, vertical_peek_ranges2d, imsplit_b, save_path, f_name[imcounts],'b')# 行，并保存   

            horizontal_sum = ti.verticalSplit(imsplit_c_deal)# c文字分割
            peek_ranges = ti.extract_peek_ranges_from_array(horizontal_sum)
            #peek_ranges_clear = ti.Clear_peekrangesclear(peek_ranges)
            vertical_peek_ranges, vertical_peek_ranges2d = ti.extract_peek_source(peek_ranges, imsplit_c_deal)# 列
            ti.imgEachType(peek_ranges, vertical_peek_ranges2d, imsplit_c, save_path, f_name[imcounts],'c')# 行，并保存
            '''
            # 内存回收
            del (image_sour, image_deal, image_lines,draw_img,box,image_result,cropped,imsplit_a, 
                imsplit_b, imsplit_c,horizontal_sum,peek_ranges,vertical_peek_ranges, vertical_peek_ranges2d)
            gc.collect()

            time_end=time.time()
            time_all += time_end - time_start
            time_ = time.strftime('%H:%M:%S', time.gmtime(time_end - time_start))           
            time_all_ = time.strftime('%H:%M:%S', time.gmtime(time_all))          
            print("单次用时： "+ str(time_)  +"\t"+"总用时: " + str(time_all_))
            
            #cv2.namedWindow("image1",0)
            #cv2.namedWindow("image2",0)
            #cv2.namedWindow("image3",0)
            #cv2.imshow('image1', imsplit_a_deal)
            #cv2.imshow('image2', imsplit_b_deal)
            #cv2.imshow('image3', imsplit_c_deal)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
