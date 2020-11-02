#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/11/1 10:05 下午
# @Author : 郜志强
# @Version：V 0.1
# @File : funcs.py
# @desc :

import cv2
import numpy as np
import math
import warnings
import base64
from common.logger import log

warnings.filterwarnings('ignore')


def base64ChangeCv2(image_base64):
    missing_padding = 4 - len(image_base64) % 4
    if missing_padding:
        image_base64 += '=' * missing_padding
    # 将str转为bytes
    image_bytes = base64.b64decode(image_base64)
    image_nparray = np.frombuffer(image_bytes, np.uint8)
    # image_nparray = np.frombuffer(image_bytes)
    image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)
    return image


def RotateByZ(Cx, Cy, thetaZ):
    rz = thetaZ*math.pi/180.0
    outX = math.cos(rz)*Cx - math.sin(rz)*Cy
    outY = math.sin(rz)*Cx + math.cos(rz)*Cy
    return outX, outY
def RotateByY(Cx, Cz, thetaY):
    ry = thetaY*math.pi/180.0
    outZ = math.cos(ry)*Cz - math.sin(ry)*Cx
    outX = math.sin(ry)*Cz + math.cos(ry)*Cx
    return outX, outZ
def RotateByX(Cy, Cz, thetaX):
    rx = thetaX*math.pi/180.0
    outY = math.cos(rx)*Cy - math.sin(rx)*Cz
    outZ = math.sin(rx)*Cy + math.cos(rx)*Cz
    return outY, outZ

def get_pixel(p1,arr1):
    pi1 = np.dot(p1, np.array([ arr1[0] ,arr1[1], arr1[2],1], dtype=np.double))
    pi2 = pi1/pi1[2]
    return pi2

def calibrate_camera(images):
    # 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差容限0.001
    criteria = (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 30, 0.001)

    # 获取标定板角点的位置
    objp = np.zeros((8 * 8, 3), np.float32)
    objp[:, :2] = np.mgrid[0:144:8j, 0:144:8j].T.reshape(-1, 2)  # 将世界坐标系建在标定板上，所有点的Z坐标全部为0，所以只需要赋值x和y

    obj_points = []  # 存储3D点
    img_points = []  # 存储2D点

    # images = glob.glob("data/*.jpg")
    # i = 0
    log.info("读入图像{}张".format(len(images)))
    for f in images:
        # img = cv2.imread(fname)
        img = base64ChangeCv2(f)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        size = gray.shape[::-1]
        ret, corners = cv2.findChessboardCorners(gray, (8, 8), None)

        if ret:
            obj_points.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)  # 在原角点的基础上寻找亚像素角点
            # print(corners2)
            if [corners2]:
                img_points.append(corners2)
            else:
                img_points.append(corners)

            cv2.drawChessboardCorners(img, (8, 8), corners, ret)
            # i += 1;
            # cv2.imwrite('tmpImage/conimg' + str(i) + '.jpg', img)

    # 标定
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)
    # log.info("ret:", ret)
    # log.info("mtx:\n", mtx)  # 内参数矩阵
    # log.info("dist:\n", dist)  # 畸变系数   distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
    # log.info("rvecs:\n", rvecs)  # 旋转向量  # 外参数
    # log.info("tvecs:\n", tvecs)  # 平移向量  # 外参数

    return ret, mtx, dist, rvecs, tvecs


def calibrate_camera_and_lidar(XYZ, data2d, data3d, mtx, dist):

    camX, camY, CamZ = map(int, XYZ)
    camXYZ = [camX, camY, CamZ]

    points = np.empty(shape=[0,3],dtype=np.double)
    pixels = np.empty(shape=[0,2],dtype=np.double)

    for count,tup_point in enumerate(zip(data2d,data3d)):
        tmpUV,tmpXYZ = tup_point
        tmpX, tmpY, tmpZ = map(int, tmpXYZ)
        # tmpPoint = np.array([tmpX, tmpY, tmpZ])
        tmpPoint = np.array([tmpX+camX, tmpY+camY, tmpZ+CamZ])
        tmpU, tmpV = map(int, tmpUV)
        tmpPixel = np.array([tmpU, tmpV])
        log.info("第{}点雷达坐标：Lx - {},Ly - {},Lz - {}\n".format(count,tmpX, tmpY, tmpZ))
        log.info("第{}点大地坐标：X - {},Y - {},Z - {}\n".format(count,tmpX+camX, tmpY+camY, tmpZ+CamZ))
        log.info("第{}点像素坐标：U - {},V - {}\n".format(count,tmpU, tmpV))
        points = np.row_stack((points, tmpPoint))
        pixels = np.row_stack((pixels, tmpPixel))

    object_3d_points = points
    object_2d_point = pixels
    dist_coefs = dist
    # 求解相机位姿
    found, rvec, tvec = cv2.solvePnP(object_3d_points, object_2d_point, mtx, dist_coefs)
    rotM = cv2.Rodrigues(rvec)[0]
    camera_postion = -np.matrix(rotM).T * np.matrix(tvec)
    # 计算相机坐标系的三轴旋转欧拉角，旋转后可以转出世界坐标系。旋转顺序z,y,x
    thetaZ = math.atan2(rotM[1, 0], rotM[0, 0])*180.0/math.pi
    thetaY = math.atan2(-1.0*rotM[2, 0], math.sqrt(rotM[2, 1]**2 + rotM[2, 2]**2))*180.0/math.pi
    thetaX = math.atan2(rotM[2, 1], rotM[2, 2])*180.0/math.pi
    # 相机坐标系下值
    x = tvec[0]
    y = tvec[1]
    z = tvec[2]
    (x, y) = RotateByZ(x, y, -1.0 * thetaZ)
    (x, z) = RotateByY(x, z, -1.0 * thetaY)
    (y, z) = RotateByX(y, z, -1.0 * thetaX)
    Cx = x * -1
    Cy = y * -1
    Cz = z * -1
    log.info("相机相对位置 \nCx:{}\nCy:{}\nCz:{}\n".format(Cx, Cy, Cz))
    log.info("相机旋转角 \nthetaX:{}\nthetaY:{}\nthetaZ:{}\n".format(thetaX, thetaY, thetaZ))

    return rotM, Cx, Cy, Cz, thetaX, thetaY, thetaZ
