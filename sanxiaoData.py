#coding:utf-8
'''
    author='chenyong'
    time='2018/3/1'
'''

from db_engine import mongo_obj,redis_obj
from flask import request
from initTable import init
import random,json,ftlog,time
from dataStatistics import dataStatisticsObj
from player import Player
import threading



def convert(data):
    '''
    :param data: bytes类型
    :return: str 类型
    如果传入的字典里面的key value是bytes，则可以递归将里面
    的所有bytes转换为str
    '''
    if isinstance(data, bytes):
        return data.decode('utf-8')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return tuple(map(convert, data))
    if isinstance(data, list):
        return list(map(convert, data))
    return data

class sanxiaoAction(object):
    def __init__(self):
        self.mongo = mongo_obj.conn.sanxiao.playerInfo
        self.mongoGF = mongo_obj.conn.sanxiao.playerGF
        self.redis = redis_obj
        self.sanxiaoPlayerKey = "sanxiao_player" # 随机匹配的玩家集合
        self.sanxiaoHDJF = "sanxiaoHDJF" # 活动积分排行榜
        self.sanxiaoScore = "sanxiaoScore" # 战力排行榜
        self.sanxiaoRoom = "sanxiaoRoom" # 正在玩的房间 field 房间号 value openIds
        self.sanxiaoTable = "sanxiaoTable" # 正在玩的棋盘 field 房间号 value 三消数组
        self.sanxiaoStart = "sanxiaoStart" # 房间的开始时间 field 房间号 value cTime
        self.sanxiaoTableRound = "sanxiaoTableRound" # 此时回合数

    # 三消三回合中玩家的攻防属性
    def scoreKey(self,num,round):
        return "sanxiaoTableScore_%s_%s"%(num,round)

    def randomKey(self,id):
        return "sanxiaoRandomPlayer_%s" % (id)

    #三消中的血量属性
    def HPKey(self,num):
        return "sanxiaoTableHP_%s"%num

    def saveScore(self,pic,nick,gong,fang,num,host,iRound):
        oPlayer = Player(request.openId,nick,pic)
        lastNick = oPlayer.playerData.get("nick","")
        lastPic = oPlayer.playerData.get("pic","")
        lastGong = oPlayer.playerData.get("gong",0)
        lastFang = oPlayer.playerData.get("fang",0)
        HP = oPlayer.playerData.get("HP",100)
        updateInfo = {}
        if lastNick != nick:
            updateInfo["nick"] = nick
        if lastPic != pic:
            updateInfo["pic"] = pic
        if gong+fang > lastGong+lastFang:
            updateInfo["gong"] = gong
            updateInfo["fang"] = fang
            # 增加战力排行
            self.redis.zrem(self.sanxiaoScore, request.openId)
            self.redis.zadd(self.sanxiaoScore,gong+fang, request.openId)
        if updateInfo:
            oPlayer.updateData(updateInfo)
        # 增加活动积分


        #带房间号的匹配
        if num:
            if not self.redis.hexists(self.HPKey(num), request.openId):
                self.redis.hset(self.HPKey(num), request.openId, HP)
            round = self.redis.hget(self.sanxiaoTableRound,num)
            if not round:
                round = 1
            else:
                round = int(round.decode())
            self.redis.hset(self.scoreKey(num, round), request.openId, [gong, fang])
            if round == 3:
                self.redis.sadd(self.sanxiaoPlayerKey, request.openId)
                gfData = []
                for i in range(1,round+1):
                    res = self.redis.hget(self.scoreKey(num,i),request.openId)
                    gf = json.loads(res.decode())
                    gfData.append(gf)
                res = self.mongoGF.find_one({"openId":request.openId},{"data":1})
                if res:
                    pD = res.get("data",[])
                    pD.append(gfData)
                    self.mongoGF.update({"openId":request.openId},{"$set":{"data":pD}})
                else:
                    self.mongoGF.insert_one({"openId": request.openId,"data": [gfData]})
        #随机匹配
        else:
            self.redis.hset(self.scoreKey(request.openId, iRound), request.openId, [gong, fang])
            if iRound == 3:
                self.redis.sadd(self.sanxiaoPlayerKey, request.openId)
                gfData = []
                for i in range(iRound):
                    res = self.redis.hget(self.scoreKey(request.openId,iRound), request.openId)
                    gf = json.loads(res.decode())
                    gfData.append(gf)
                res = self.mongoGF.find_one({"openId": request.openId}, {"data": 1})
                if res:
                    pD = res.get("data", [])
                    pD.append(gfData)
                    self.mongoGF.update({"openId": request.openId}, {"$set": {"data": pD}})
                else:
                    self.mongoGF.insert_one({"openId": request.openId, "data": [gfData]})
        dataStatisticsObj.updateScore(num,gong+fang)

    def getPlayerRankData(self,openId):
        GF = self.redis.zscore(self.sanxiaoScore,openId)
        winCount = self.redis.zscore(self.sanxiaoHDJF,openId)
        return [int(GF),int(winCount)]

    def getScore(self,num,round,time):
        res = self.redis.hgetall(self.scoreKey(num,round))
        res = convert(res)
        HP = self.redis.hgetall(self.HPKey(num))
        HP = convert(HP)
        data = {}
        for i in HP:
            if i != request.openId:
                break
        if len(res) == 2:
            res[request.openId] = json.loads(res[request.openId])
            res[request.openId].append(HP[request.openId])
            data["me"] = res[request.openId]
            res[i] = json.loads(res[i])
            res[i].append(HP[i])
            data["other"] = res[i]
            rRonud = self.redis.hget(self.sanxiaoTableRound, num)
            data["round"] = round + 1
            if not rRonud or round == int(rRonud.decode()):
                x = int(res[request.openId][0])-int(res[i][1])
                hp1 = int(HP[i])-(x if x>0 else 0)# 剩下的血量
                self.redis.hset(self.HPKey(num),i,hp1)
                y = int(res[i][1]) - int(res[request.openId][0])
                hp2 = int(HP[request.openId]) - (y if y > 0 else 0)
                self.redis.hset(self.HPKey(num), request.openId, hp2)
                self.redis.hset(self.sanxiaoTableRound,num,round+1)
                if round == 3 or hp1 <= 0 or hp2 <= 0:
                    equal = False
                    if hp2 > hp1:
                        winId = request.openId
                        loseId = i
                    elif hp1 > hp2:
                        winId = i
                        loseId = request.openId
                    else:
                        winId = request.openId
                        loseId = i
                        equal = True
                    self.winLose(winId,loseId,equal)
                    self.redis.zincrby(name=self.sanxiaoHDJF, amount=1, value=winId)
            else:
                pass

            threading.Thread(target=self.waitDelete, args=(num,))
            return data
        elif time<5:
            return False
        elif len(res) == 1:
            if request.openId in res:
                res[request.openId] = json.loads(res[request.openId])
                res[request.openId].append(HP[request.openId])
                data["me"] = res[request.openId]
            else:
                data["me"] =[0,0,HP[request.openId]]
            data["other"] = [0,0,HP[i]]
            res[i] = [0,0]
            rRonud = self.redis.hget(self.sanxiaoTableRound, num)
            data["round"] = round + 1
            if not rRonud or round == int(rRonud.decode()):
                x = int(res[request.openId][0]) - int(res[i][1])
                hp1 = int(HP[i]) - (x if x > 0 else 0)  # 剩下的血量
                self.redis.hset(self.HPKey(num), i, hp1)
                y = int(res[i][1]) - int(res[request.openId][0])
                hp2 = int(HP[request.openId]) - (y if y > 0 else 0)
                self.redis.hset(self.HPKey(num), request.openId, hp2)
                self.redis.hset(self.sanxiaoTableRound, num, round + 1)
                if round == 3 or hp1 <= 0 or hp2 <= 0:
                    equal = False
                    if hp2 > hp1:
                        winId = request.openId
                        loseId = i
                    elif hp1 > hp2:
                        winId = i
                        loseId = request.openId
                    else:
                        winId = request.openId
                        loseId = i
                        equal = True
                    self.winLose(winId,loseId,equal)
                    self.redis.zincrby(name=self.sanxiaoHDJF, amount=1, value=winId)
                    threading.Thread(target=self.waitDelete,args=(num,))
            return data

    def winLose(self,winId,loseId,equal=False):
        winPlayer = Player(winId)
        losePlayer = Player(loseId)
        if equal:
            winPlayer.winGoal(50) # 战斗打平奖励
            losePlayer.winGoal(50)
        else:
            winPlayer.winGoal(100)  # 战斗胜利奖励
            losePlayer.winGoal(20)  # 战斗失败奖励

    def calcHP(self):
        pass

    def waitDelete(self,num):
        time.sleep(5)
        self.deleteRoomTable(num)

    def deleteRoomTable(self,num):
        self.redis.hdel(self.sanxiaoRoom,num)
        self.redis.hdel(self.sanxiaoTable, num)
        self.redis.hdel(self.sanxiaoStart,num)
        self.redis.hdel(self.sanxiaoTableRound,num)
        for i in range(1,4):
            self.redis.delete(self.scoreKey(num,i))
        self.redis.delete(self.HPKey(num))
        ftlog.info(num,request.openId)

    def getRandomPlayer(self,round,choosePlayer=False):
        # 随机匹配时选中玩家
        if choosePlayer:
            while True:
                n = self.redis.scard(self.sanxiaoPlayerKey)
                if n <= 1:
                    newPlayer = self.makeNewPlayer()
                else:
                    openId = self.redis.srandmember(self.sanxiaoPlayerKey, 1)
                    openId = openId[0].decode()
                    if openId == request.openId:
                        continue
                    res = self.mongoGF.find_one({"openId": openId}, {"data": 1})
                    GFData = res.get("data", [])
                    if not GFData:
                        continue
                    iLen = len(GFData)
                    GF = GFData[random.randint(0, iLen - 1)]
                    self.redis.hset(self.randomKey(request.openId), "GF", GF)
                    self.redis.hset(self.randomKey(request.openId), "id", openId)
                    randomPlayer = Player(openId)
                    nick = randomPlayer.playerData.get("nick", "")
                    pic = randomPlayer.playerData.get("pic", "")
                    newPlayer = [nick,pic]
                return newPlayer
        else:
            res = self.redis.hgetall(self.randomKey(request.openId))
            res = convert(res)
            openId = res["id"]
            otherGF = json.loads(res["GF"])[round-1]
            meData  = self.redis.hget(self.scoreKey(request.openId,round),request.openId)
            if not meData:
                meData = [0,0]
            else:
                meData = json.loads(convert(meData))
            data = {}
            data["me"] = meData
            data["other"] = otherGF
            data["round"] = round + 1
            randomPlayer = Player(openId)
            nick = randomPlayer.playerData.get("nick","")
            pic = randomPlayer.playerData.get("pic","")
            newPlayer = [nick,pic,data]
            if round == 3:
                for i in range(1,round+1):
                    self.redis.delete(self.scoreKey(request.openId, i))
                self.redis.delete(self.randomKey(request.openId))
            return newPlayer

    def getRandomTable(self):
        table = init()
        return table

    def makeNewPlayer(self):
        return ["picture","nick"]

    def getRanking(self,type,num):
        if type == "score":
            res = self.redis.zrange(self.sanxiaoScore,5*(num-1),5*num-1,desc=True,withscores=True)
            res = convert(res)
            data = []
            for i in res:
                oPlayer = Player(i[0])
                nick = oPlayer.playerData.get("nick")
                pic = oPlayer.playerData.get("pic")
                info = [nick,pic,i[1]]
                data.append(info)
            return data
        elif type == "jifen":
            res = self.redis.zrange(self.sanxiaoHDJF,5*(num-1),5*num-1,desc=True, withscores=True)
            res = convert(res)
            data = []
            for i in res:
                oPlayer = Player(i[0])
                nick = oPlayer.playerData.get("nick")
                pic = oPlayer.playerData.get("pic")
                info = [nick, pic, i[1]]
                data.append(info)
            return data
        else:
            pass

    def getRandomRoom(self,openId):
        exist = True
        num = ""
        while exist:
            num = ""
            for i in range(4):
                num += str(random.randint(0, 9))
            if not self.redis.hexists(self.sanxiaoRoom,num) and not self.redis.hexists(self.sanxiaoTable,num) and \
                not self.redis.hexists(self.sanxiaoStart,num):
                exist =False
        self.redis.hset(self.sanxiaoRoom,num,openId+":::")
        return num

    def isMatchSuccess(self,num):
        openId = self.redis.hget(self.sanxiaoRoom,num)
        if openId:
            openIds = openId.decode().split(":::")
            ftlog.info("isMatch", openIds, request.openId)
            if len(openIds) == 2 and openIds[0] == request.openId and openIds[1] != "":
                res = self.mongo.find_one({"openId":openIds[1]},{"pic":1,"nick":1})
                if not res:
                    return -2,"",""
                nick = res.get("nick")
                pic = res.get("pic")
                dataStatisticsObj.startRoom(num)
                return self.getNewTable(num),nick,pic
        return -1,"",""

    def isJoinMatchSuccess(self,num):
        openId = self.redis.hget(self.sanxiaoRoom, num)
        if openId:
            openIds = openId.decode().split(":::")
            ftlog.info("joinMatch", openIds, request.openId)
            if len(openIds) == 2 and openIds[1] == request.openId:
                res = self.mongo.find_one({"openId": openIds[0]}, {"pic": 1, "nick": 1})
                if not res:
                    return -2,"",""
                nick = res.get("nick")
                pic = res.get("pic")
                return self.getNewTable(num),nick,pic
            else:
                return -1,"",""
        else:
            return -2,"",""

    def getNewTable(self,num,next=False):
        newTable = self.redis.hget(self.sanxiaoTable, num)
        if not newTable:
            newTable = init()
            self.redis.hset(self.sanxiaoTable, num, {"table":newTable,"round":0})
        elif next:
            newTable = convert(newTable)
            newTable = json.loads(newTable.replace("\'", "\""))
            if newTable["round"] == str(next) or newTable["round"] == int(next):
                return newTable["table"]
            else:
                newTable = init()
                self.redis.hset(self.sanxiaoTable, num, {"table": newTable, "round": next})
        else:
            newTable = convert(newTable)
            newTable = json.loads(newTable.replace("\'","\""))["table"]
        return newTable

    def getNextTable(self,num,round):
        openId = self.redis.hget(self.sanxiaoRoom, num)
        if openId:
            openIds = openId.decode().split(":::")
            rRound = self.redis.hget(self.sanxiaoTableRound,num)
            if request.openId in openIds and int(rRound.decode()) == round:
                newTable = self.getNewTable(num,round)
                return newTable
            else:
                return False
        else:
            return False

    def setOpenId(self,num,nick,pic):
        openId = self.redis.hget(self.sanxiaoRoom, num)
        if openId:
            openIds = openId.decode().split(":::")
            if len(openIds) == 2 and (openIds[1] == '' or openIds[1] == request.openId):
                newOpenIds = openIds[0] + ":::" + request.openId
                self.redis.hset(self.sanxiaoRoom,num,newOpenIds)
                return True
            else:
                return False
        else:
            return False

    def isStart(self,host,num):
        res = self.redis.hget(self.sanxiaoTable, num)
        res1 = self.redis.hget(self.sanxiaoRoom, num)
        if res and res1:
            openIds = res1.decode().split(":::")
            if host:
                if request.openId == openIds[0]:
                    startTime = int(time.time())+5
                    self.redis.hset(self.sanxiaoStart,num,startTime)
                    return startTime
            else:
                if request.openId == openIds[1]:
                    res = self.redis.hget(self.sanxiaoStart,num)
                    if res:
                        return res.decode()
                    else:
                        return False
        else:
            return False

sanxiaoObj = sanxiaoAction()

if  __name__ == "__main__":
    sanxiaoObj.getRandomRoom("3431rsgasg")
