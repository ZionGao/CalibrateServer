#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/11/1 10:42 下午
# @Author : 郜志强
# @Version：V 0.1
# @File : test.py
# @desc :
import requests
import json
import base64
import glob

pics = glob.glob('data/*.jpg')


def get_base64_fromImg(img_path):
    f = open(img_path, 'rb')
    base64_data = base64.b64encode(f.read())
    return base64_data.decode()


data1 = {'token': 1234,
         'prjId': 1234,
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

_ = requests.post('http://127.0.0.1:5000/CalibrateCamera', data=json.dumps(data1))
result = json.loads(_.text)
print(result)

data2 = {'token': 1234,
         'prjId': 1234,
         "para": result['result'],
         "BLH": {"X": "0", "Y": "0", "Z": "0"},
         "coordinateData0": [
             {"seq": "0", "axisX": "0", "axisY": "0", "axisZ": "0"},
             {"seq": "1", "axisX": "1", "axisY": "1", "axisZ": "1"},
             {"seq": "2", "axisX": "2", "axisY": "2", "axisZ": "2"},
             {"seq": "3", "axisX": "3", "axisY": "3", "axisZ": "3"},
             {"seq": "4", "axisX": "4", "axisY": "4", "axisZ": "4"},
             {"seq": "5", "axisX": "5", "axisY": "5", "axisZ": "5"}
         ],
         "coordinateData1": [
             {"seq": "0", "axisX": "0", "axisY": "0"},
             {"seq": "1", "axisX": "1", "axisY": "1"},
             {"seq": "2", "axisX": "2", "axisY": "2"},
             {"seq": "3", "axisX": "3", "axisY": "3"},
             {"seq": "4", "axisX": "4", "axisY": "4"},
             {"seq": "5", "axisX": "5", "axisY": "5"}
         ],
         }

_ = requests.post('http://127.0.0.1:5000/CalibrateCameraAndLidar', data=json.dumps(data2))
result = json.loads(_.text)
print(result)