#coding:utf-8
'''
    author='chenyong'
    time='2018/1/26'
'''

from flask import request,jsonify
from db_engine import redis_obj
from baseConfig import thirdKey
import time
import ftlog

def before_request():
    '''
    params = request.json
    status = checkParams(params,list(params.keys()))
    if not status:
        real_ip = request.headers.get('X-Forwarded-For', "")
        if len(real_ip.split(",")) > 1:
            reqIp = real_ip.split(",")[1]
        else:
            reqIp = real_ip

        return jsonify({"code": -1001, "msg": "status error", "data": {}})
    '''
    if "login" in request.url:
        pass
    else:
        res = request.json
        if not res:
            return jsonify({"code": -1003, "msg": "jsondata not exist", "data": {}})
        third = request.json.get("third","")
        if third:
            if not isinstance(third,str):
                third = ""
            res = redis_obj.get(thirdKey+"_"+third)
            if res:
                openId, session_key = res.decode().split("::")
                request.openId = openId
            else:
                return jsonify({"code":-1001,"msg":"third is not exist","data":{}})
        else:
            return jsonify({"code": -1001, "msg": "third is not exist", "data": {}})


def blackList():
    real_ip = request.headers.get('X-Forwarded-For', "")
    if len(real_ip.split(",")) > 1:
        reqIp = real_ip.split(",")[1]
    else:
        reqIp = real_ip



def checkParams(params={},keys=[]):
    if not isinstance(params,dict):
        return False
    for i in params.keys():
        if i not in keys or not isinstance(i,str):
            return False
        if not createRoomParamsCheck(i,params):
            return False
    if unMD5(params):
        return True

def createRoomParamsCheck(k,params):
    if k == "type":
        if isinstance(params[k],str):
            return True
    elif k == "count":
        if isinstance(params[k],int):
            return True
    elif k == "num":
        if isinstance(params[k],int):
            return True
    elif k == "third":
        if isinstance(params[k], str):
            return True
    elif k == "time":
        if isinstance(params[k],int):
            return True
    elif k == "code":
        if isinstance(params[k], str):
            return True
    print(k,"is error")


def unMD5(data):
    import _md5
    s = ''
    pw = "dasfqdasfafa1e32" # 秘钥
    if 'time' not in data:
        ftlog.info("status time error")
        return False
    if isinstance(data['time'],int) and 0 <= int(time.time())-data['time'] <= 2:
        keys = list(data.keys())
        keys.sort()
        for k in keys:
            if k == "code":
                continue
            s += k + str(data[k])
        s += pw
        if data["code"] == _md5.md5(s.encode()).hexdigest():
            return True
        else:
            ftlog.info("status code error")
    return False

def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Methods'] = "POST"
    response.headers['Access-Control-Allow-Headers'] = "x-requseted-with,content-type"
    response.headers["Content-type"] = "application/json"
    if hasattr(request,"need_unlock"):
        for i in request.need_unlock:
            redis_obj.delete(i)
            request.need_unlock.remove(i)
    return response