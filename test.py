#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/11/1 10:42 下午
# @Author : 郜志强
# @Version：V 0.1
# @File : test.py
# @desc :
import requests
import json
import time
import re
import base64
import sys
import glob


pics = glob.glob('data/*.jpg')

def get_base64_fromImg(img_path):
    f = open(img_path, 'rb')
    base64_data = base64.b64encode(f.read())
    return base64_data.decode()
    #print('data:image/jpeg;base64,%s'%s)


data1 = { 'token' : 1234,
          'prjId' : 1234,
         "image": [
             {
                 "imageID": "1220",
                 "imageBase64": get_base64_fromImg(pics[0])
             },
             {
                 "imageID": "1221",
                 "imageBase64": get_base64_fromImg(pics[1])
             }
         ]
         }

start_time = time.time()
_ = requests.post('http://127.0.0.1:5000/CallibrateCamera', data=json.dumps(data1))
print(_)
end_time = time.time()
interval = end_time - start_time
print("time:", interval)
result = json.loads(_.text)
print(result)
