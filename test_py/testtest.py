from functools import reduce
import requests, json

def f(x):
    return x*x

def add(x, y):
    return x + y

def fn(x, y):
    return x * 10 + y

def char2num(s):
    digits = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
    return digits[s]

DIGITS = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}

def str2int(s):
    def fn(x, y):
        return x * 10 + y
    def char2num(s):
        return DIGITS[s]
    return reduce(fn, map(char2num, s))

def is_odd(n):
    return n % 2 == 1

def not_empty(s):
    return s and s.strip()

def _odd_iter():
    n = 1
    while True:
        n = n + 2
        yield n

def lazy_sum(*args):
    def sum():
        ax = 0
        for n in args:
            ax = ax + n
        return ax
    return sum

def count():
    def f(j):
        def g():
            return j*j
        return g
    fs = []
    for i in range(1, 4):
        fs.append(f(i))
    return fs

def count():
    def f(j):
        def g():
            return j*j
        return g
    fs = []
    for i in range(1, 4):
        fs.append(f(i))
    return fs

def build(x):
    return lambda: x*x

def now():
    print('2018-3-28')


class Student(object):
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

def student2dict(std):
    return {
        'name' : std.name,
        'age' : std.age,
        'score' : std.score
    }

def dict2student(d):
    return Student(d['name'], d['age'], d['score'])

def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('c ... %s' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('p ... %s' % n)
        r = c.send(n)
        print('return : %s' % r)
    c.close()






