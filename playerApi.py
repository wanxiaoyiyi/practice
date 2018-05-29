#coding:utf-8
'''
    author='chenyong'
    time='2018/3/26'
'''
from flask import request,jsonify,Blueprint
from player import Player
playerApi = Blueprint('player', __name__, url_prefix='/sanxiao/player')

@playerApi.route("/refresh",methods=["POST"])
def refresh():
    info = Player(request.openId).playerInfo()
    return jsonify({"code":"1000","msg":"ok","data":info})

@playerApi.route("/testTili",methods=["POST"])
def buyItem():
    count = request.json.get("count",0)
    oPlayer = Player(request.openId)
    oPlayer.addIncTiLi(count)
    return jsonify({"code": 1000, "msg": "add ok", "data": ""})
