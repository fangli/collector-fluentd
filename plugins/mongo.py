#!/usr/bin/env python
# -*- coding:utf-8 -*-

# *********************************************************#
# @@ScriptName: mongo.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-10 10:16:52
# @@Modify Date: 2014-03-13 18:44:40
# @@Function:
# *********************************************************#


import sys
import time
import urllib2

try:
    from libs import minjson
except ImportError:
    import minjson


def printStats(metric, ts, value, tag=""):
    if value is not None:
        print "mongo.%s %i %s %s" % (metric.lower(), int(ts), str(value), str(tag))


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
    try:
        ss = getServerStatus()
    except:
        sys.exit()

    # Get opcounters
    for k, v in ss["opcounters"].iteritems():
        printStats('opcounters.' + str(k), ts, str(v), "cf_datatype=counter")

    # Get Memory loc
    for k, v in ss["mem"].iteritems():
        if memItems(k):
            printStats("mem." + str(k), ts, str(v), "cf_datatype=gauge")

    # Print current connections
    printStats("connections.count", ts, str(ss["connections"]["current"]), "cf_datatype=gauge")


if __name__ == "__main__":
    doData()
