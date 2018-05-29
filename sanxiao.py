from flask import Flask,request,jsonify,Blueprint
from db_engine import redis_obj
from check import before_request,after_request
from sanxiaoData import sanxiaoObj
from useItem import item
from playerApi import playerApi
from player import Player
from baseConfig import appId,secret,thirdKey
from initTable import init
import requests,json
app = Flask(__name__)

sanxiao = Blueprint('sanxiao', __name__, url_prefix='/sanxiao')
'''
    小程序：三消
    排行榜 getRanking
    玩家成绩 playerScore
'''
@sanxiao.route('/login',methods=["POST"])
def login():
    import _md5
    code = request.json.get("code","")
    wxUrl = "https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code" \
            % (appId, secret, code)

    res = requests.get(wxUrl)

    data = json.loads(res.text)
    session_key = data.get("session_key", "")
    openid = data.get("openid", "")
    if not session_key or not openid:
        return jsonify({"code": -1002, "msg": "get third error", "data": data})
    nick = request.json.get("nick", "")
    pic = request.json.get("pic", "")

    Player(openid, nick, pic) # init player

    ss = "azxswqedc"+session_key+openid
    third = _md5.md5(ss.encode()).hexdigest()
    redis_obj.set(thirdKey+"_"+third,openid+"::"+session_key)
    redis_obj.expire(thirdKey+"_"+third,3600*12)
    return jsonify({"code":200,"msg":"get third","data":{"third":third}})

@sanxiao.route('/match',methods=["POST"])
def match():
    num = request.json.get("num","")
    host = int(request.json.get("host",0))
    if host:
        res,nick,pic = sanxiaoObj.isMatchSuccess(num)
    else:
        res,nick,pic = sanxiaoObj.isJoinMatchSuccess(num)

    if res == -1:
        return jsonify({"code": -1001, "msg": "match fail", "data": {"table":res,"nick":nick,"pic":pic}})
    elif res == -2 :
        return jsonify({"code": -1002, "msg": "room close", "data": {"table":res,"nick":nick,"pic":pic}})
    else:
        return jsonify({"code": 1000, "msg": "match success", "data": {"table":res,"nick":nick,"pic":pic}})

@sanxiao.route('/destroyRoom',methods=["POST"])
def destroyRoom():
    num = request.json.get("num","")
    sanxiaoObj.deleteRoomTable(num)
    return jsonify({"ok":1})

@sanxiao.route('/setOpenId',methods=["POST"])
def setOpenId():
    num = request.json.get("num","")
    nick = request.json.get("nick")
    pic = request.json.get("pic")
    res = sanxiaoObj.setOpenId(num,nick,pic)
    if res:
        return jsonify({"code":1000,"msg":"setOpenId success","data": []})
    else:
        return jsonify({"code": -1001, "msg": "setOpenId fail", "data": []})

@sanxiao.route('/getTable',methods=["POST"])
def getTable():
    newTable1 = init()
    return jsonify({"code":1000,"msg":"getTable success","data":newTable1})

@sanxiao.route('/getNextTable',methods=["POST"])
def getNextTable():
    num = request.json.get("num","")
    round = request.json.get("round",1)
    data = sanxiaoObj.getNextTable(num,round)
    if data:
        return jsonify({"code": 1000, "msg": "getNextTable success", "data": data})
    else:
        return jsonify({"code": -1001, "msg": "getNextTable fail", "data": []})

@sanxiao.route('/getScore',methods=["POST"])
def getScore():
    num = request.json.get("num","")
    round = request.json.get("round", 2)
    times = request.json.get("times",1)
    score = sanxiaoObj.getScore(num,round,times)
    if score:
        return jsonify({"code":1000,"msg":"getScore success","data":score})
    else:
        return jsonify({"code": -1001, "msg": "getScore success", "data": []})

@sanxiao.route('/start',methods=["POST"])
def start():
    num = request.json.get("num")
    host = int(request.json.get("host"))
    res = sanxiaoObj.isStart(host,num)
    if res:
        return jsonify({"code":1000,"msg":"isStart success","data":res})
    else:
        return jsonify({"code": -1001, "msg": "isStart fail", "data": []})

@sanxiao.route('/getPlayerScore',methods=["POST"])
def getRandomScore():
    round = request.json.get("round",1)
    player = sanxiaoObj.getRandomPlayer(round)
    return jsonify({"code":1000,"msg":"","data":player})

@sanxiao.route('/getPlayerTable',methods=["POST"])
def getRandomTable():
    player = sanxiaoObj.getRandomPlayer(1,True)
    table = sanxiaoObj.getRandomTable()
    return jsonify({"code":1000,"msg":"","data":{"newPlayer":player,"table":table}})

@sanxiao.route('/saveScore',methods=["POST"])
def saveScore():
    gong = request.json.get('gong',0)
    fang = request.json.get("fang",0)
    pic = request.json.get('pic',"")
    nick = request.json.get("nick","")
    num = request.json.get("num","")
    round = request.json.get("round", 1)
    host = int(request.json.get("host",0))
    sanxiaoObj.saveScore(pic,nick,gong,fang,num,host,round)
    return jsonify({"code": 1000, "msg": "save ok", "data":""})

@sanxiao.route('/getRanking',methods=["POST"])
def getRanking():
    type = request.json.get("type","")
    num = request.json.get("num",1)
    data = sanxiaoObj.getRanking(type,num)
    return jsonify({"code": 1000, "msg": "save ok", "data":data})

@sanxiao.route('/test',methods=["GET"])
def test():
    return jsonify({"code": 1000, "msg": "save ok"})

@sanxiao.route('/getRoomNum',methods=["POST"])
def getRandomRoomNum():
    num = sanxiaoObj.getRandomRoom(request.openId)
    return jsonify({"code": 1000, "msg": "save ok", "data":num})

@sanxiao.route('/getPlayerRankData',methods=["POST"])
def getPlayerRankData():
    data = sanxiaoObj.getPlayerRankData(request.openId)
    return jsonify({"code": 1000, "msg": "save ok", "data":data})

app.register_blueprint(sanxiao)
app.register_blueprint(item)
app.register_blueprint(playerApi)
app.before_request(before_request)
app.after_request(after_request)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=8082,debug=True)
