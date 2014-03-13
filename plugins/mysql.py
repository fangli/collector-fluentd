#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: mysql.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-09 10:57:34
# @@Modify Date: 2014-03-13 15:48:07
# @@Function: Statistics from a default MySQL instance
#*********************************************************#

"""Statistics from a default MySQL instance.

Note: this collector parses your MySQL "show global status", and outputs all
      None-zero value to TSD

"""

import time
import sys
import subprocess


INCLUDE_KEYS = {
    "questions": "counter",
    "queries": "counter",
    "innodb.log.write.requests": "counter",
    "innodb.dblwr.pages.written": "counter",
    "innodb.dblwr.writes": "counter",
    "select.range": "counter",
    "innodb.row.lock.time": "counter",
    "bytes.sent": "counter",
    "bytes.received": "counter",
    "innodb.buffer.pool.pages.free": "gauge",
    "innodb.buffer.pool.pages.data": "gauge",
    "innodb.buffer.pool.pages.dirty": "gauge",
    "innodb.buffer.pool.pages.flushed": "gauge",
    "innodb.buffer.pool.pages.misc": "gauge",
    "innodb.buffer.pool.pages.total": "gauge",
    "innodb.buffer.pool.reads": "gauge",
    "innodb.buffer.pool.write.requests": "counter",
    "innodb.buffer.pool.read.requests": "counter",
    "handler.write": "counter",
    "handler.commit": "counter",
    "handler.delete": "counter",
    "handler.rollback": "counter",
    "handler.update": "counter",
    "handler.read.first": "counter",
    "handler.read.key": "counter",
    "handler.read.next": "counter",
    "handler.read.prev": "counter",
    "handler.read.rnd": "counter",
    "handler.read.rnd.next": "counter",
    "innodb.rows.read": "counter",
    "aborted.clients": "counter",
    "aborted.connects": "counter",
    "connections": "counter",
    "flush.commands": "gauge",
    "innodb.data.fsyncs": "counter",
    "innodb.data.read": "counter",
    "innodb.data.written": "counter",
    "innodb.data.reads": "counter",
    "innodb.data.writes": "counter",
    "innodb.pages.created": "counter",
    "innodb.pages.read": "counter",
    "innodb.pages.written": "counter",
    "innodb.row.lock.time.avg": "gauge",
    "innodb.row.lock.time.max": "gauge",
    "innodb.row.lock.waits": "gauge",
    "innodb.rows.deleted": "counter",
    "innodb.rows.inserted": "counter",
    "innodb.rows.updated": "counter",
    "key.blocks.unused": "gauge",
    "key.blocks.used": "gauge",
    "key.read.requests": "counter",
    "key.reads": "counter",
    "key.write.requests": "counter",
    "key.writes": "counter",
    "max.used.connections": "gauge",
    "open.files": "gauge",
    "open.table.definitions": "gauge",
    "open.tables": "gauge",
    "select.scan": "counter",
    "slow.queries": "counter",
    "sort.rows": "counter",
    "threads.cached": "gauge",
    "threads.connected": "gauge",
    "threads.created": "gauge",
    "threads.running": "gauge",
}
    

def printStats(metric, ts, value, tag=""):
    if value is not None:
        print "mysql.%s %i %s %s" % (metric, int(ts), str(value), tag)


def getMysqlClient():
    _proc = subprocess.Popen(
        ["which", "mysql"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = _proc.communicate()
    if _proc.returncode != 0:
        return None
    else:
        return stdout.strip()


def getStats():
    stats = {}
    mysql_cli = getMysqlClient()
    if mysql_cli is None:
        print >> sys.stderr, "MySQL not detected: No mysql client found"
        return {}

    _proc = subprocess.Popen(
        [mysql_cli, "--batch", "-e", "show global status"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = _proc.communicate()
    if _proc.returncode != 0:
        print >> sys.stderr, "MySQL return with none zero: %r" % _proc.returncode
        return {}

    for line in stdout.split("\n"):
        raw_metric = line.split()
        if (
            len(raw_metric) > 1
            and raw_metric[1].isdigit()
            and raw_metric[1] != "0"
        ):
            stats[raw_metric[0].replace('_', '.').lower()] = raw_metric[1]

    return stats


def main():
    stats = getStats()
    ts = time.time()
    for st in stats.keys():
        if st in INCLUDE_KEYS.keys():
            printStats(st, ts, stats[st], "cf_datatype=" + INCLUDE_KEYS[st].strip())

if __name__ == "__main__":
    main()
