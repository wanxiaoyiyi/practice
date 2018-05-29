#coding:utf-8
'''
    author='chenyong'
    time='2018/3/23'
'''
from flask import request,jsonify,Blueprint
from player import Player
item = Blueprint('item', __name__, url_prefix='/sanxiao/item')

@item.route("/useItem",methods=["POST"])
def useItem():
    id = request.json.get('id',0)
    oPlayer = Player(request.openId)
    oPlayer.useItem(id)

@item.route("/buyItem",methods=["POST"])
def buyItem():
    id = request.json.get("id",0)
    count = request.json.get("count",0)
    oPlayer = Player(request.openId)
    oPlayer.addItem(id,count)
    return jsonify({"code": 1000, "msg": "add ok", "data": ""})

@item.route("/bag",methods=["POST"])
def bag():
    oPlayer = Player(request.openId)
    return jsonify({"code":1000,"msg":"bag","data":oPlayer.bag})


