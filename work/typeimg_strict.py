import cv2
import os
import numpy as np
from matplotlib import pyplot as plt

#垂直分割
def verticalSplit(img):
    adaptive_threshold = img 
    horizontal_sum = np.sum(adaptive_threshold, axis=0)
    #plt.plot(horizontal_sum, range(horizontal_sum.shape[0]))
    #plt.gca().invert_yaxis()
    #plt.show()
    return horizontal_sum

#文字切割
def extract_peek_ranges_from_array(array_vals, minimun_val=1000, minimun_range=2):
    start_i = None
    end_i = None
    peek_ranges = []

    for i, val in enumerate(array_vals):
        if val > minimun_val and start_i is None:
            start_i = i
        elif val > minimun_val and start_i is not None:
            pass
        elif val < minimun_val and start_i is not None:
            end_i = i
            if end_i - start_i >= minimun_range:
                peek_ranges.append((start_i, end_i))
            start_i = None
            end_i = None
        elif val < minimun_val and start_i is None:
            pass
        else:
            raise ValueError("cannot parse this case...")

    #print(peek_ranges,type(peek_ranges))
    
    #对文字分割进行整理，去除上下结构分割错误

    #imsplit_a,imsplit_b用值
    #a_len = 10 #两字间距
    #a_len_e = 15 #例如“ 一二 ”的两字间距更大一点
    #b_len = 18 #单字高度最低限 """
    
    #imsplit_c用值
    a_len = 5 #两字间距
    a_len_e = 15 #例如“ 一二 ”的两字间距更大一点
    b_len = 18 #大部分单字高度最低限

    #合并上下结构文字
    peek_ranges_new = []
    peek_ranges = np.array(peek_ranges)
    peek_ranges = peek_ranges.flatten()
    if len(peek_ranges):
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
    if len(peek_ranges):
        peek_ranges_new.append(peek_ranges[len(peek_ranges)-1])

    #合并 “二”
    peek_ranges_new1 = []
    flag=0
    end_flag=0
    end_temp=0
    for i in range(len(peek_ranges_new)):
        if(flag==0): 
            if(peek_ranges_new[i+1] - peek_ranges_new[i] > b_len):#判断是否是结构件（包括 “一” ） （>：否， <：是）
                if(end_flag == 1):#标志位判断上一个是否是结构件，识别类似结构件高度的文字 （例如“一”）
                    end_flag = 0
                    end_temp = peek_ranges_new[i - 1]
                    peek_ranges_new1.append(end_temp)
                peek_ranges_new1.append(peek_ranges_new[i])
                peek_ranges_new1.append(peek_ranges_new[i+1])
            else:
                if(end_flag == 0): #识别两个以上结构件
                    end_flag = 1
                    peek_ranges_new1.append(peek_ranges_new[i])
                    end_temp = peek_ranges_new[i+1]
    
                elif(end_flag == 1 and peek_ranges_new[i] - peek_ranges_new[i-1] < b_len): #判断间距，两个结构件
                    end_temp = peek_ranges_new[i+1]

                elif(end_flag == 1 and peek_ranges_new[i] - peek_ranges_new[i-1] >= a_len_e): #判断间距，两个文字
                    peek_ranges_new1.append(end_temp)
                    end_flag = 0

                    peek_ranges_new1.append(peek_ranges_new[i])
                    end_temp = peek_ranges_new[i+1]   
                    end_flag = 1

                if(end_flag == 1 and i==(len(peek_ranges_new)-2)):
                    peek_ranges_new1.append(end_temp) 
            flag = 1
        else:
            flag -=1
            
    # 一维数组升维
    flag=0
    peek_ranges_clear=[]
    for i in range(len(peek_ranges_new1)-1):
        if(flag==0):
            peek_ranges_clear.append((peek_ranges_new1[i],peek_ranges_new1[i+1]))
            flag = 2
        flag -= 1
    #print(peek_ranges_clear,type(peek_ranges_clear))

    return peek_ranges_clear

#水平分割
def extract_peek_source(peek_ranges, img):   
    adaptive_threshold = img

    line_seg_adaptive_threshold = np.copy(adaptive_threshold)
    for i, peek_range in enumerate(peek_ranges):
        x = peek_range[0]
        y = 0
        w = peek_range[1]
        h = line_seg_adaptive_threshold.shape[0]
        pt1 = (x, y)
        pt2 = (x + w, y + h)
        cv2.rectangle(line_seg_adaptive_threshold, pt1, pt2, 255)
    #cv2.imshow('line image', line_seg_adaptive_threshold)
    #cv2.waitKey(0)

    vertical_peek_ranges2d = []
    vertical_peek_ranges = []
    for peek_range in peek_ranges:
        start_x = 0
        end_x = line_seg_adaptive_threshold.shape[0]
        line_img = adaptive_threshold[start_x:end_x,peek_range[0]:peek_range[1]]

        #cv2.imshow('binary image', line_img)

        vertical_sum = np.sum(line_img, axis=1)

        #plt.plot(vertical_sum, range(vertical_sum.shape[0]))
        #plt.gca().invert_yaxis()
        #plt.show()

        vertical_peek_ranges = extract_peek_ranges_from_array(vertical_sum,minimun_val=2,minimun_range=1)
        vertical_peek_ranges2d.append(vertical_peek_ranges)

    #print(vertical_peek_ranges2d)
    return vertical_peek_ranges, vertical_peek_ranges2d
#判断b，c区域识别个数是否相等，否 则丢弃
def deal_vertical_peek_ranges2d(vertical_peek_ranges2d, peek_ranges):
    new_vertical_peek_ranges2d=[]
    new_peek_ranges=[]
    btoc = 1410 # 1410为b c分隔的绝对位置

    for list_1 in range(len(vertical_peek_ranges2d)):
        b_size = 0
        c_size = 0
        for list_2 in range(len(vertical_peek_ranges2d[list_1])):
            if(vertical_peek_ranges2d[list_1][list_2][0] < btoc): 
                b_size += 1
            elif(vertical_peek_ranges2d[list_1][list_2][0] > btoc):
                c_size += 1     
        #print(b_size, " ", c_size)
        if(b_size == c_size):
            new_vertical_peek_ranges2d.append(vertical_peek_ranges2d[list_1])
            new_peek_ranges.append(peek_ranges[list_1])

    #print(new_vertical_peek_ranges2d)
    return new_vertical_peek_ranges2d, new_peek_ranges

#判断选择后，拼合合格的列
def imageCompose(new_peek_ranges, img, row_height):
    col_width = 0
    position_width = 20
    print("len(new_peek_ranges):",len(new_peek_ranges))
    for i in range(len(new_peek_ranges)):
        col_width += (new_peek_ranges[i][1]-new_peek_ranges[i][0])

    col_width += len(new_peek_ranges)*20 + 20 #每列间隔20像素

    # 新建图
    img_temp = img.copy()
    new_img = img_temp[:row_height, 0 : col_width]
    new_img = cv2.rectangle(new_img, (0, 0), (col_width, row_height), (255, 255, 255), -1)

    #cv2.imshow("1", img)
    #cv2.imshow("2", img)
    cv2.waitKey (0)
    print(new_peek_ranges)
    for i in range(len(new_peek_ranges)):

        src2 = img[:, new_peek_ranges[i][0] : new_peek_ranges[i][1]] #每一列切割
        position_width_temp = position_width + (new_peek_ranges[i][1] - new_peek_ranges[i][0])
        #plt.imshow(new_img)
        #plt.imshow(src2)
        #plt.show()
        
        new_img[:, position_width:position_width_temp] = src2 #指定位置填充，大小要一样才能填充 
        position_width = position_width_temp + 20

    #cv2.imshow("合成", new_img)
    #cv2.waitKey (0)

    return new_img

# 分割出每列的文字
def imgEachType(peek_ranges, vertical_peek_ranges2d, adaptive_threshold, save_path, f_name, block1, block2, new_img_B, new_img_C):
    image_color = adaptive_threshold
    cnt = 1
    row_b = 1 #行（从上向下）
    row_c = 1
    col_b = len(vertical_peek_ranges2d) #列（从右向左）
    col_c = len(vertical_peek_ranges2d)

    color = (0, 0, 255)
    if (not os.path.exists(save_path+block1+"_full"+'/')):           
    # 创建c目录操作函数
        os.makedirs(save_path+block1+"_full"+'/') 
    cv2.imwrite(save_path + block1+"_full"+'/'+'m_01_'+ f_name+'_'+block1+"_full" +'.jpg', new_img_B) #写

    if (not os.path.exists(save_path+block2+"_full"+'/')):           
    # 创建c目录操作函数
        os.makedirs(save_path+block2+"_full"+'/') 
    cv2.imwrite(save_path + block2+"_full"+'/'+'m_01_'+ f_name+'_'+block2+"_full" +'.jpg', new_img_C) #写

    for i, peek_range in enumerate(peek_ranges):#输出b
        for vertical_range in vertical_peek_ranges2d[i]:
            x = peek_range[0]
            y = vertical_range[0]
            w = peek_range[1] - x
            h = vertical_range[1] - y
            # print(str(x)+'-'+str(y)+'-'+str(w)+'-'+str(h))

            # 如果不存在则创建目录
            if (not os.path.exists(save_path+block1+'/')):           
                # 创建b目录操作函数
                os.makedirs(save_path+block1+'/')
            if (not os.path.exists(save_path+block2+'/')):           
                # 创建c目录操作函数
                os.makedirs(save_path+block2+'/') 
            
            if(w * h > 190 and w > 15 and h > 5):# 若裁剪像素过小则跳过
                patch = adaptive_threshold[y:y+h,x:x+w]
                if(vertical_range[0] < 1410):
                    cv2.imwrite(save_path + block1+'/'+'m_01_'+f_name+'_'+block1+'_'+'%d' %col_b+'_'+'%d' %row_b+'.jpg', patch) #写
                if(vertical_range[0] > 1410):
                    cv2.imwrite(save_path + block2+'/'+'m_01_'+f_name+'_'+block2+'_'+'%d' %col_c+'_'+'%d' %row_c+'.jpg', patch) #写
                cnt += 1
                pt1 = (x, y)
                pt2 = (x + w, y + h)
                row_b += 1 
                row_c += 1
            

        row_b = 1
        row_c = 1
        col_b -= 1 
        col_c -= 1
    #cv2.rectangle(image_color, pt1, pt2, color)
    #cv2.imshow('char image', image_color)
    #cv2.waitKey(0)
