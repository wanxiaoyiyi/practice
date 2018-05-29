#coding:utf-8
'''
    author='chenyong'
    time='2018/1/26'
'''

import redis,pymongo
from db_engine.config import online,username,password,CONN_ADDR1,CONN_ADDR2,REPLICAT_SET,mongo_db,redis_db

redis_obj = redis.StrictRedis(**redis_db)

class Mongo_DB(object):
    def __init__(self):
        if online:
            self.conn = pymongo.MongoClient([CONN_ADDR1, CONN_ADDR2], port=27017, replicaSet=REPLICAT_SET)
            self.conn.admin.authenticate(username, password)
        else:
            self.conn = pymongo.MongoClient(**mongo_db)

mongo_obj = Mongo_DB()
