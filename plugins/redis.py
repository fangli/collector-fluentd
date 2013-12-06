#!/usr/bin/env python
# -*- coding:utf-8 -*-

# *********************************************************#
# @@ScriptName: redis.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-09 10:57:34
# @@Modify Date: 2013-12-06 11:46:44
# @@Function: Statistics from a default Redis instance
# *********************************************************#


"""
Statistics from a Redis instance.
"""

import time
import re
import sys
import subprocess


METRICS = [
    "bgrewriteaof_in_progress", "bgsave_in_progress", "blocked_clients",
    "changes_since_last_save", "connected_clients", "expired_keys",
    "keyspace_hits", "keyspace_misses", "total_commands_processed",
    "total_connections_received", "uptime_in_seconds", "used_cpu_sys",
    "used_cpu_user", "used_memory", "used_memory_rss"
]


def printStats(metric, ts, value, tags):
    if value is not None:
        print "redis.%s %i %s %s" % (metric, int(ts), str(value), tags)


def getRedisClient():
    _proc = subprocess.Popen(
        ["which", "redis-cli"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = _proc.communicate()
    if _proc.returncode != 0:
        return None
    else:
        return stdout.strip()


def getStats(port):
    stats = {}
    redis_cli = getRedisClient()
    if redis_cli is None:
        print >> sys.stderr, "redis-cli not detected: No redis client found"
        return {}

    _proc = subprocess.Popen(
        [redis_cli, "-p", str(port), "info"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = _proc.communicate()
    if _proc.returncode != 0:
        print >> sys.stderr, "redis return with none zero: %r" % _proc.returncode
        return {}

    for line in stdout.split("\n"):
        raw_metric = line.split(":")
        if (
            len(raw_metric) > 1
            and (raw_metric[0] in METRICS)
        ):
            stats[raw_metric[0].replace('_', '.').lower()] = raw_metric[1].strip()

    return stats


def scanInstances():
    """Use netstat to find instances of Redis listening on the local machine, then
    figure out what configuration file they're using to name the cluster.
    Current function Written by Mark Smith <mark@qq.is>.
    """

    out = {}
    tcre = re.compile(r"^\s*#\s*tcollector.(\w+)\s*=\s*(.+)$")

    ns_proc = subprocess.Popen(
        ["netstat", "-tnlp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = ns_proc.communicate()
    if ns_proc.returncode != 0:
        print >> sys.stderr, "failed to find instances %r" % ns_proc.returncode
        return {}

    for line in stdout.split("\n"):
        if not (line and 'redis-server' in line):
            continue
        pid = int(line.split()[6].split("/")[0])
        port = int(line.split()[3].split(":")[1])

        # now we have to get the command line.  we look in the redis config file for
        # a special line that tells us what cluster this is.  else we default to using
        # the port number which should work.
        cluster = "port-%d" % port
        try:
            f = open("/proc/%d/cmdline" % pid)
            cfg = f.readline().split("\0")[-2]
            f.close()

            f = open(cfg)
            for cfgline in f:
                result = tcre.match(cfgline)
                if result and result.group(1).lower() == "cluster":
                    cluster = result.group(2).lower()
        except EnvironmentError:
            # use the default cluster name if anything above failed.
            pass

        out[port] = cluster
    return out


def main():
    instances = scanInstances()
    ts = time.time()
    for port in instances.keys():
        stats = getStats(port)
        for st in stats.keys():
            printStats(st, ts, stats[st], "port=%i" % port)

if __name__ == "__main__":
    main()
