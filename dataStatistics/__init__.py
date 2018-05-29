#coding:utf-8
'''
    author='chenyong'
    time='2018/3/12'
'''
import os,sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(path)
sys.path.append(path)
from db_engine import mongo_obj
from flask import request
import time

class DataStatistics(object):
    def __init__(self):
        self.sanxiaoStatistics = mongo_obj.conn.sanxiaoStatistics

    def startRoom(self,num):
        insertData = {
            "openId":request.openId,
            "startTime":int(time.time()),
            "num":num
        }
        self.sanxiaoStatistics.startRoom.insert_one(insertData)

    def updateScore(self,num,score):
        endTime = int(time.time())
        condition = {"openId":request.openId,"num":num,"startTime":{"$gte":endTime-210,"$lte":endTime-30}}
        self.sanxiaoStatistics.startRoom.update(condition,{"$set":{"score.%s"%request.openId:score}})

    def getDayRoomCount(self,cTime):
        day = time.strftime("%Y%m%d",time.localtime(cTime))
        start = time.mktime(time.strptime(day,"%Y%m%d"))
        end = start + 86400
        print(start,end)
        return start,end

    def testInsert(self):
        for i in range(30):
            startTime = int(time.time())-i*86400
            for j in range(1000):
                self.sanxiaoStatistics.startRoom.insert_one({"startTime":startTime,"j":j,"fasfas":"fasgasgasrqwr"})

    def testfind(self):
        start,end = self.getDayRoomCount(int(time.time()))
        res = self.sanxiaoStatistics.startRoom.find({"startTime":{"$gt":start,"$lt":end}})
        print(self.sanxiaoStatistics.startRoom.count({"startTime":{"$gt":start,"$lt":end}}))

dataStatisticsObj = DataStatistics()

if __name__ == "__main__":
    obj = DataStatistics()
    obj.getDayRoomCount(int(time.time()))
    now = int(time.time())
    obj.testInsert()
    now1 = int(time.time())
    print(now1-now)
    obj.testfind()
    now2 = int(time.time())
    print(now2-now)
