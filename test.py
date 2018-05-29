#coding:utf-8
'''
    author='chenyong'
    time='2018/3/1'
'''
import redis,time,requests
import random
'''
res = requests.post("http://127.0.0.1:8082/sanxiao/login",json={"type":"score","num":1
,"third":"864552a9ded3b168cbcd2f5430e6ab53"})

print(res.text)



res = requests.post("http://127.0.0.1:8082/sanxiao/saveScore",json={"gong":50,"fang":25,"round":3
,"third":"864552a9ded3b168cbcd2f5430e6ab53"})

print(res.text)
'''
res = requests.post("http://127.0.0.1:8082/sanxiao/getPlayerScore",json={"round":1
,"third":"864552a9ded3b168cbcd2f5430e6ab53"})

print(res.text)
print(random.randint(0,100))
a=1