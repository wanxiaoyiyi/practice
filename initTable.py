#coding:utf-8
'''
    author='chenyong'
    time='2018/2/26'
'''

from config import WITCH,HEIGHT,COLORTYPE


newTable = None

allTable = []

def init1():
    global newTable
    newTable = [[-1 for i in range(WITCH)] for j in range(HEIGHT)]
    for i in range(WITCH):
        for j in range(HEIGHT):
            flag = True
            while flag:
                newTable[i][j] = getRandomType()
                res = checkPoint(i,j)
                if res:
                    flag = False

# 获取一个新三消盘
def init():
    global newTable,allTable
    allTable = []
    for i in range(20):
        init1()
        for j in newTable:
            allTable.append(j)
    newTable1 = []
    for i in allTable:
        for j in i:
            newTable1.append(j)
    return newTable1

def checkPoint(i,j,trace=True):
    shang = j-1
    xia = j+1
    zuo = i-1
    you = i+1
    if 0<=i<=WITCH-1 and 0<=j<=HEIGHT-1:
        if 0<=shang<=HEIGHT-1 and 0<=xia<=HEIGHT-1 and newTable[i][j] != -1:
            if newTable[i][shang] == newTable[i][j] and newTable[i][j] == newTable[i][xia]:
                return False
        if 0<=zuo<=WITCH-1 and 0<=you<=WITCH-1:
            if newTable[zuo][j] == newTable[i][j] and newTable[i][j] == newTable[you][j]:
                return False
    if trace:
        result = checkPoint(i,shang,False)
        if not result:
            return False
        result = checkPoint(i, xia, False)
        if not result:
            return False
        result = checkPoint(zuo, j, False)
        if not result:
            return False
        result = checkPoint(you, j, False)
        if not result:
            return False
    return True

def getRandomType():
    import random
    color = random.randint(0,COLORTYPE-1)
    return color


def checkXiao():
    for i in range(WITCH):
        for j in range(HEIGHT-2):
            if newTable[i][j] == newTable[i][j+1] and newTable[i][j+1] == newTable[i][j+2]:
                print("error",i,j)
                print(newTable)
    for j in range(HEIGHT):
        for i in range(WITCH-2):
            if newTable[i][j] == newTable[i+1][j] and newTable[i+1][j] == newTable[i+2][j]:
                print("error",i,j)
                print(newTable)

if __name__ == "__main__":
    init()
    print(allTable)
    init()
    print(len(allTable))









