#coding:utf-8
'''
    author='chenyong'
    time='2018/1/30'
'''
import requests
res = requests.get("http://127.0.0.1:6111/wxpay/pay")
print(res.text)
import selectors