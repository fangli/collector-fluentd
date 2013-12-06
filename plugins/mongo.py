#!/usr/bin/env python
# -*- coding:utf-8 -*-

# *********************************************************#
# @@ScriptName: mongo.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-10 10:16:52
# @@Modify Date: 2013-12-06 11:46:35
# @@Function:
# *********************************************************#


import time
import urllib2
try:
    from libs import minjson
except ImportError:
    import minjson


def printStats(metric, ts, value):
    if value is not None:
        print "mongo.%s %i %s" % (metric.lower(), int(ts), str(value))


def memItems(s):
    return (
        s == "resident"
        or s == "virtual"
        or s == "mapped"
        or s == "mappedWithJournal"
    )


def getServerStatus():
    raw = urllib2.urlopen("http://127.0.0.1:28017/_status").read()
    return minjson.read(raw)["serverStatus"]


def doData():
    ts = time.time()
    ss = getServerStatus()

    # Get opcounters
    for k, v in ss["opcounters"].iteritems():
        printStats('opcounters.' + str(k), ts, str(v))

    # Get Memory loc
    for k, v in ss["mem"].iteritems():
        if memItems(k):
            printStats("mem." + str(k), ts, str(v))

    # Print current connections
    printStats("connections.count", ts, str(ss["connections"]["current"]))


if __name__ == "__main__":
    doData()
