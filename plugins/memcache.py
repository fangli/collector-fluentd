#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: memcache.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-10 10:03:21
# @@Modify Date: 2014-03-28 18:53:36
# @@Function: collector plugin for memcache
#*********************************************************#

import socket
import subprocess
import sys


# Those are the stats we MUST collect at every COLLECTION_INTERVAL.
COUNTER_STATS = [
    "cmd_get", "cmd_set", "total_connections",
    "get_hits", "get_misses",
    "delete_misses", "delete_hits",
    "bytes_read", "bytes_written", "bytes",
    "total_items", "evictions",
]

GAUGE_STATS = [
    "curr_connections",
    "curr_items",
    "uptime",
]

DATASETS = {
    11211: "11211",
    11212: "11212",
    11213: "11213",
    11214: "11214",
    11215: "11215",
}


def find_memcached():
    """Yields all the ports that memcached is listening to, according to ps."""
    p = subprocess.Popen(["pgrep", "-lf", "memcached"], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    assert p.returncode in (0, 1), "pgrep returned %r" % p.returncode
    for line in stdout.split("\n"):
        if not line:
            continue
        line = line + " "
        port = line.find(" -p ")
        if port < 0:
            print >>sys.stderr, "Weird memcached process without a -p argument:", line
            continue
        port = line[port + 4: line.index(" ", port + 5)]
        port = int(port)
        if port in DATASETS:
            yield port
        else:
            print >>sys.stderr, "Unknown memached port:", port


def collect_stats(sock):
    """Sends the 'stats' command to the socket given in argument."""
    sock.send("stats\r\n")
    stats = sock.recv(1024)
    stats = [line.rstrip() for line in stats.split("\n")]
    assert stats[-1] == "", repr(stats)
    assert stats[-2] == "END", repr(stats)
    # Each line is of the form: STAT statname value
    stats = dict(line.split()[1:3] for line in stats[:-2])
    stats["time"] = int(stats["time"])
    return stats


def main(args):
    """Collects and dumps stats from a memcache server."""
    sockets = {}  # Maps a dataset name to a socket connected its memcached.
    for port in find_memcached():
        dataset = DATASETS[port]
        sockets[dataset] = socket.socket()
        sockets[dataset].connect((socket.gethostname(), port))
    if not sockets:
        return 13  # No memcached server running.

    stats = {}  # Maps a dataset name to a dict that maps a stats to a value.

    def print_stat(stat, dataset, datatype):
        print ("memcache.%s %d %s port=%s cf_datatype=%s"
               % (stat, stats[dataset]["time"], stats[dataset][stat], dataset, datatype))

    for dataset, sock in sockets.iteritems():
        stats[dataset] = collect_stats(sock)

        # Print all the important stats first.
        for stat in COUNTER_STATS:
            print_stat(stat, dataset, "counter")
        for stat in GAUGE_STATS:
            print_stat(stat, dataset, "gauge")

    sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
