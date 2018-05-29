'''
    author='chenyong'
    time='2017/12/7'
'''
import datetime
import sys

LOG_LEVEL_DEBUG = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_ERROR = 2

ipConfig = {
    "10.0.7.233": 0,
    "10.0.7.234": 1,
    "10.10.179.3": 0,
}

def getIp():
    import socket
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr

log_level = ipConfig.get(getIp(),0)

def _log(*argl, **kwargs):
    _log_msg = (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))+" "
    _log_msg += sys._getframe().f_back.f_back.f_code.co_name + "  "
    for l in argl:
        if type(l) == tuple:
            ps = str(l)
        else:
            try:
                ps = "%r" % l
            except:
                try:
                    ps = str(l)
                except:
                    ps = 'ERROR LOG OBJECT'
        if type(l) == str:
            _log_msg += ps[1:-1] + ' '
        else:
            _log_msg += ps + ' '
    if len(kwargs) > 0:
        _log_msg += str(kwargs)
    return _log_msg

def info(*argl, **kwargs):
    if log_level > LOG_LEVEL_INFO:
        return
    print(_log(*argl,**kwargs))

def debug(*argl,**kwargs):
    if log_level > LOG_LEVEL_DEBUG:
        return
    print(_log(*argl,**kwargs))

def error(*argl,**kwargs):
    if log_level > LOG_LEVEL_ERROR:
        return
    argl=["error"]+list(argl)
    print(_log(*argl,**kwargs))

