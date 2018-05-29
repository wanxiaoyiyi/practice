#coding:utf-8
'''
    author='chenyong'
    time='2018/3/1'
'''

from initTable import init,newTable
from db_engine import redis_obj
import gevent

matchKey = "sanxiaoMatchQueue"
matchTime = "sanxiaoMatchTime"
matchFinish = "sanxiaoMatchFinish"
matchPlayerKey = "matchPlayer"

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

def matchPlayer(id):
    lock_name = "matchlock" # 队列锁
    lock = redis_obj.setnx(lock_name, 1)
    if lock:
        # 获得锁设置超时时间
        redis_obj.expire(lock_name, 1)
        request.need_unlock.append(lock_name)
    else:
        count = 0
        while True:
            count += 1
            lock = redis_obj.setnx(lock_name, 1)
            if lock:
                redis_obj.expire(lock_name, 1)
                break
            if count == 20:
                return jsonify({"code":-1003,"data":{}})
            print(id,count)
            gevent.sleep(0.1)

    hasMatch = redis_obj.hget(matchFinish, id)
    if hasMatch:
        redis_obj.hdel(matchFinish,id)
        return jsonify({"code": 1000, "data": convert(hasMatch)})
    while True:
        onePlayer = redis_obj.lpop(matchKey)
        if not onePlayer or onePlayer.decode() == id:
            redis_obj.rpush(matchKey,id)
            redis_obj.hset(matchTime,id,int(time.time()))
            return jsonify({"code":-1003,"data":{}})
        if not isMatching(onePlayer.decode()):
            continue
        else:
            init()
            oneTable = newTable
            redis_obj.hset(matchFinish,onePlayer.decode(),oneTable)
            redis_obj.hset(matchPlayerKey,onePlayer.decode(),id)
            redis_obj.hset(matchPlayerKey,id,onePlayer.decode())
            return jsonify({"code": 1001, "data": oneTable})

def isMatching(id):
    iTime = int(redis_obj.hget(matchTime,id).decode())
    now = int(time.time())
    redis_obj.hdel(matchTime, id)
    if now-iTime <=2:
        return True
    else:
        return False


