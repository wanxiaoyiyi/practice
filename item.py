#coding:utf-8
'''
    author='chenyong'
    time='2018/3/23'
'''

import ftlog


class Item(object):
    def __init__(self):
        self.item = None
        self.mongo = mongo_obj.conn.sanxiao.playerInfo

    def reload(self):
        pass

    def useItem(self,openId,item,count):
        res = self.mongo.find_one({"openId":openId},{"bag.%s"%item:1})
        if res:
            hasCount = res.get("bag",{}).get(item,0)
            if int(hasCount) < count:
                return False
            else:
                self.mongo.update({"openId":openId},)

                ftlog.info(openId, item, count)
        else:
            return False
