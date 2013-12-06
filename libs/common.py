#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: common.py
# @@Author: Felix Lee <surivlee@gmail.com>
# @@Create Date: 12/26/2012
# @@Modify Date: 2013-12-06 11:41:54
# @@Function:
#*********************************************************#

__author__ = "Felix Lee <surivlee@gmail.com>"
__version__ = (0, 1)


import time
import config as conf


def log(message, level=0):
    if level == -1:
        sLevel = '[DEBUG]'
    elif level == 0:
        sLevel = '[INFO]'
    elif level == 1:
        sLevel = '[WARNING]'
    elif level == 2:
        sLevel = '[CRITICAL]'
    else:
        sLevel = '[FATAL]'

    if conf.LOG_LEVEL.lower() == "debug":
        level_defined = -1
    elif conf.LOG_LEVEL.lower() == "info":
        level_defined = 0
    elif conf.LOG_LEVEL.lower() == "warning":
        level_defined = 1
    elif conf.LOG_LEVEL.lower() == "critical":
        level_defined = 2
    else:
        level_defined = 3

    if level >= level_defined:
        try:
            with open(conf.LOG_FILE, 'a') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + sLevel + ' ' + message + '\n')
        except:
            pass


