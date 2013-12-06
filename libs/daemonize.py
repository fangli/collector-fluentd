#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: daemonize.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-12-05 14:21:57
# @@Modify Date: 2013-12-06 11:44:30
# @@Function:
#*********************************************************#

import os
import __main__


# The following class comes from https://github.com/thesharp/daemonize
def daemonize():
    """Performs the necessary dance to become a background daemon."""

    cwd = os.path.dirname(os.path.realpath(__main__.__file__))

    if os.fork():
        os._exit(0)
    os.chdir(cwd)
    os.umask(022)
    os.setsid()
    os.umask(0)
    if os.fork():
        os._exit(0)
    stdin = open(os.devnull)
    stdout = open(os.devnull, 'w')
    os.dup2(stdin.fileno(), 0)
    os.dup2(stdout.fileno(), 1)
    os.dup2(stdout.fileno(), 2)
    stdin.close()
    stdout.close()
    for fd in xrange(3, 1024):
        try:
            os.close(fd)
        except OSError:
            pass

def writePid(pidfile):
    """Write our pid to a pidfile."""
    f = open(pidfile, "w")
    try:
        f.write(str(os.getpid()))
    except:
        pass
    f.close()

def getPid():
    """Get current PID"""
    return int(os.getpid())
