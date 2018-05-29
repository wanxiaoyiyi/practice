#coding:utf-8
'''
    author='chenyong'
    time='2018/3/20'
'''

from db_engine import mongo_obj
import time
import ftlog

class Player(object):
    def __init__(self,openId,nick="",pic=""):
        self.mongo_obj = mongo_obj.conn.sanxiao.playerInfo
        self.playerData = self.mongo_obj.find_one({"openId":openId})
        self.openId = openId
        self.tiliRecover = 300 # 体力恢复的时间
        self.tLMax = 5 # 体力的最大值
        self.initGoal = 100 # 初始化金币的数量

        if not self.playerData:
            # 初始化玩家数据
            now = int(time.time())
            initData = {"openId":openId,"nick":nick,"pic":pic,"tl":5,"tlTime":now,\
                        "createTime":now,"HP":100,"gong":0,"fang":0,"bag":{}}
            self.addInitData(initData)
            self.mongo_obj.insert_one(initData)
            self.playerData = initData
        self.bag = self.playerData.get("bag", {})

    def playerInfo(self):
        data = {}
        addTL = self.calcTiLi()
        hasTL = self.playerData.get("tl",5)
        if hasTL<5:
            if addTL > 0:
                hasTL = self.tLMax if hasTL+addTL>=5 else hasTL+addTL
                self.playerData["tl"] = hasTL
                self.updateData({"tl":hasTL})
                self.updateData({"tlTime":int(time.time())})
        data["tl"] = hasTL
        data["goal"] = self.playerData.get("goal",0)
        data["bag"] = self.bag
        return data

    def calcTiLi(self):
        now = int(time.time())
        tlTime = self.playerData.get("tlTime",now)
        if now - tlTime > 0:
            return (now-tlTime)//self.tiliRecover
        else:
            return 0

    def addInitData(self,initData):
        initData["goal"] = self.initGoal

    def updateData(self,data={}):
        self.mongo_obj.update({"openId": self.openId}, {"$set":data})

    def winGoal(self,count):
        iCount = self.playerData.get("goal",0)
        self.updateData({"goal":iCount+count})

    def useItem(self,id,count):
        hasCount = self.bag.get(id,0)
        if hasCount<count:
            return False
        else:
            self.addItem(id,-count)
            ftlog.info(self.openId,id,count)
            return True

    def addItem(self,item,count):
        hasCount = self.bag.get(item,0)
        self.mongo_obj.update({"openId":self.openId},{"$set":{"bag.%s"%item:hasCount+count}})
        ftlog.info(self.openId,item,count)

    # 购买体力或者消耗体力
    def addIncTiLi(self,count=1):
        hasCount = self.playerData.get("tl", 0)
        self.mongo_obj.update({"openId": self.openId}, {"$set": {"tl": hasCount + count}})
        ftlog.info(self.openId,count)

if __name__ == "__main__":
    a = Player("chenyong")
