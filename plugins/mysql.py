#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: mysql.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-09 10:57:34
# @@Modify Date: 2014-02-25 11:59:57
# @@Function: Statistics from a default MySQL instance
#*********************************************************#

"""Statistics from a default MySQL instance.

Note: this collector parses your MySQL "show global status", and outputs all
      None-zero value to TSD

"""

import time
import sys
import subprocess


IGNORE_KEYS = ["com.", "created."]


def printStats(metric, ts, value):
    if value is not None:
        print "mysql.%s %i %s" % (metric, int(ts), str(value))


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
        is_ignore = False
        for ignore in IGNORE_KEYS:
            if (st.startswith(ignore)):
                is_ignore = True
        if not is_ignore:
            printStats(st, ts, stats[st])

if __name__ == "__main__":
    main()
