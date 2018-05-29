#coding:utf-8
'''
    author='chenyong'
    time='2018/1/26'
'''
online = False

CONN_ADDR1 = "dds-2ze3a9b84da79c841.mongodb.rds.aliyuncs.com:3717"  # 节点1
CONN_ADDR2 = "dds-2ze3a9b84da79c842.mongodb.rds.aliyuncs.com:3717"  # 节点2
REPLICAT_SET = 'mgset-4403913'  # 副本集名称
username = 'root'
password = 'smilePassw0rd'
port = 27017

# 非节点链接
mongo_db = dict(
    host="0.0.0.0",
    port=27017,
)

redis_db = dict(
    host="0.0.0.0",
    port=6379,
    db=4,
)

def getIp():
    import socket
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr

ip = getIp()
if ip == "10.10.179.3":
    online = False