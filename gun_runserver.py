import gevent.monkey
gevent.monkey.patch_all()
import multiprocessing

debug = True
loglevel = 'debug'
bind = '0.0.0.0:8082'
logfile = '~/wxsmallGame/log/practice/debug.log'
errorlog = "~/wxsmallGame/log/practice/error.log"
accesslog = "~/wxsmallGame/log/practice/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
capture_output = True
keepalive = 5
test_variable = 'test'
#启动的进程数
workers = multiprocessing.cpu_count()+1
worker_class = 'gevent'

x_forwarded_for_header = 'X-FORWARDED-FOR'
