# encoding: utf-8
import sys
import urllib, base64
import urllib.request
import json
import re

def get_token(API_Key,Secret_Key):
    # 获取access_token
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+API_Key+'&client_secret='+Secret_Key
    req = urllib.request.Request(host)
    req.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(req)
    content = response.read()
    content_json=json.loads(content)
    access_token=content_json['access_token']
    return access_token


def recognition_word_high(filepath,filename,access_token):
    url='https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=' + access_token
    # 二进制方式打开图文件
    f = open(filepath + filename, 'rb')  # 二进制方式打开图文件
    # 参数image：图像base64编码
    img = base64.b64encode(f.read())
    params = {"image": img}
    params = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url, params)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urllib.request.urlopen(req)
    content = response.read()
    print(content)
    if (content):
        # print(content)
        world=re.findall('"words": "(.*?)"}',str(content),re.S)
        print(world)
        for each in world:
            print(each)

if __name__ == '__main__':

    API_Key = "XXX" #API_Key百度云创建应用（文字识别）获得
    Secret_Key = "XXX" #Secret_Key
    filepath = "D:/Users/84460/Desktop/Oracle_Split/Picture/01/"
    filename="0001.png"
    access_token=get_token(API_Key,Secret_Key)
    recognition_word_high=recognition_word_high(filepath,filename,access_token)