from flask import Flask
import numpy as np
import seaborn as sns; sns.set()
from easydict import EasyDict
from collections import OrderedDict
from flask import Flask, make_response, request,json
from flask_cors import *
from common.logger import log
from source.funcs import callibrate_camera

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    data = EasyDict({'name': 'calibrate_server', 'version': 1.0})
    return get_result_response(data)


@app.route('/CallibrateCamera',methods=['POST'])
def batch():
    res = {"state": "99",
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
                return json.dumps(res, ensure_ascii=False)
            code.append(id)
            image_str.append(img)
        log.info("Successful Transfer of Pictures")
    except Exception as e:
        log.error(e)
        res['msg'] = 'The server receives a bad json'
        return get_result_response(EasyDict({
            res
        }))
    log.info("ip:{}".format(request.remote_addr))

    ret, mtx, dist, rvecs, tvecs = callibrate_camera(image_str)

    result = {"ret": ret, "mtx": mtx.tolist(), "dist": dist.tolist(), "rvecs": list(map(np.ndarray.tolist, rvecs)),
              "tvecs": list(map(np.ndarray.tolist, tvecs))}
    res["result"] = result

    return get_result_response(EasyDict(
        res
    ))


def get_result_response(msg):
    response = make_response(msg)
    response.headers["Content-Type"] = "application/json"
    response.headers["name"] = "calibrate_server"
    return response




if __name__ == '__main__':
    app.run()
