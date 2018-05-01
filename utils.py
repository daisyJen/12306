# -*- coding:utf-8 -*-
import datetime
import time
from dateutil import parser
GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800'
# 生成datetime对象的过程和我可能不同，这里是拿当前时间来生成
# print datetime.datetime.utcnow().strftime(GMT_FORMAT)

def strToGMT(time_string):
    datetime_struct = parser.parse(time_string)
    return datetime.datetime.strftime(datetime_struct, GMT_FORMAT)
