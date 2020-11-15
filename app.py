import numpy as np
import seaborn as sns;

sns.set()
from easydict import EasyDict
from flask import Flask, make_response, request, json
from flask_cors import *
from common.logger import log
from source.funcs import calibrate_camera, calibrate_camera_and_lidar

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    data = EasyDict({'name': 'calibrate_server', 'version': 1.0})
    return get_result_response(data)


@app.route('/CalibrateCamera', methods=['POST'])
def calibrateCamera():
    res = {"code": "99",
           "msg": "",
           "result": {}}
    code = []
    image_str = []
    try:
        data = json.loads(request.get_data(as_text=True))
        token = data['token']
        prjId = data['prjId']
        image_string = data['image']
        for i in image_string:
            id = i['imageID']
            img = i['imageBase64']
            if id == "" or img == "":
                res['msg'] = "recived bad pics"
                return json.dumps(get_result_response(EasyDict(
                    res
                )), ensure_ascii=False)
            code.append(id)
            image_str.append(img)
        log.info("Successful Transfer of Pictures")
    except Exception as e:
        log.error(e)
        res['msg'] = 'The server receives a bad json'
        return get_result_response(EasyDict(
            res
        ))
    log.info("ip:{}".format(request.remote_addr))

    ret, mtx, dist, rvecs, tvecs = calibrate_camera(image_str)

    result = {"ret": ret, "mtx": mtx.tolist(), "dist": dist.tolist(), "rvecs": list(map(np.ndarray.tolist, rvecs)),
              "tvecs": list(map(np.ndarray.tolist, tvecs))}
    res["result"] = result
    res["code"] = "00"
    res["msg"] = "Success"

    return get_result_response(EasyDict(
        res
    ))


@app.route('/CalibrateCameraAndLidar', methods=['POST'])
def calibrateCameraAndLidar():
    res = {"code": "99",
           "msg": "",
           "result": {}}
    data2d = []
    data3d = []
    xyz = (0, 0, 0)
    try:
        data = json.loads(request.get_data(as_text=True))
        token = data['token']
        prjId = data['prjId']
        raw3d = data['coordinateData0']
        raw2d = data['coordinateData1']
        xyz = (float(data['BLH']["x"]), float(data['BLH']["y"]), float(data['BLH']["z"]))
        mtx = np.array(data["para"]["mtx"])
        dist = np.array(data["para"]["dist"])

        assert (len(raw2d) == len(raw3d)), "接收坐标对数据长度不一致"
        assert (len(raw2d) >= 6), "接收坐标对数据长度小于6"

        for i in range(0, len(raw2d)):
            tmpraw2dU = float(raw2d[i]["axisX"])
            tmpraw2dV = float(raw2d[i]["axisY"])

            tmpraw3dX = float(raw3d[i]["axisX"])
            tmpraw3dY = float(raw3d[i]["axisY"])
            tmpraw3dZ = float(raw3d[i]["axisZ"])

            data2d.append((tmpraw2dU, tmpraw2dV))
            data3d.append((tmpraw3dX, tmpraw3dY, tmpraw3dZ))

        log.info("Successful transfer of points")
    except Exception as e:
        log.error(e)
        res['msg'] = 'The server receives a bad json'
        return get_result_response(EasyDict(
            res
        ))
    log.info("ip:{}".format(request.remote_addr))

    rotM, tvec, rvec, Cx, Cy, Cz, thetaX, thetaY, thetaZ = calibrate_camera_and_lidar(xyz, data2d, data3d, mtx, dist)

    result = {"rotM": list(map(np.ndarray.tolist, rotM)),
              "tvec": list(map(np.ndarray.tolist, tvec)),
              "rvec": list(map(np.ndarray.tolist, rvec)),
              "Cx": Cx.tolist()[0],
              "Cy": Cy.tolist()[0],
              "Cz": Cz.tolist()[0],
              "thetaX": thetaX,
              "thetaY": thetaY,
              "thetaZ": thetaZ}

    res["result"] = result
    res["code"] = "00"
    res["msg"] = "Success"

    return get_result_response(EasyDict(
        res
    ))


def get_result_response(msg):
    response = make_response(msg)
    response.headers["Content-Type"] = "application/json"
    response.headers["name"] = "calibrate_server"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9010)
