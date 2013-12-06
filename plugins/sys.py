#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: sys.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-09 16:40:48
# @@Modify Date: 2013-12-06 11:46:46
# @@Function:
#*********************************************************#

# This file is part of tcollector.
# Copyright (C) 2010  The tcollector Authors.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
#
"""import various /proc stats from /proc into TSDB"""


import re
import sys
import time


def main():
    f_uptime = open("/proc/uptime", "r")
    f_meminfo = open("/proc/meminfo", "r")
    f_vmstat = open("/proc/vmstat", "r")
    f_stat = open("/proc/stat", "r")
    f_loadavg = open("/proc/loadavg", "r")
    f_entropy_avail = open("/proc/sys/kernel/random/entropy_avail", "r")

    # Uptime
    f_uptime.seek(0)
    ts = int(time.time())
    for line in f_uptime:
        m = re.match("(\S+)\s+(\S+)", line)
        if m:
            print "sys.uptime.total %d %s" % (ts, m.group(1))
            print "sys.uptime.now %d %s" % (ts, m.group(2))

    # proc.meminfo
    f_meminfo.seek(0)
    ts = int(time.time())
    mem_types = [
        "memtotal",
        "memfree",
        "buffers",
        "cached",
        "swapcached",
        "active",
        "inactive",
        "swaptotal",
        "swapfree",
        "dirty",
        "writeback",
        "anonpages",
        "mapped",
    ]
    for line in f_meminfo:
        m = re.match("(\w+):\s+(\d+)", line)
        if m and m.group(1).lower() in mem_types:
            print (
                "sys.memory.%s %d %s" % (m.group(1).lower(), ts, m.group(2))
            )

    # proc.vmstat
    f_vmstat.seek(0)
    ts = int(time.time())
    for line in f_vmstat:
        m = re.match("(\w+)\s+(\d+)", line)
        if not m:
            continue
        if m.group(1) in ("pgpgin", "pgpgout", "pswpin",
                          "pswpout", "pgfault", "pgmajfault"):
            print "sys.vmstat.%s %d %s" % (m.group(1), ts, m.group(2))

    # proc.stat
    f_stat.seek(0)
    ts = int(time.time())
    for line in f_stat:
        m = re.match("(\w+)\s+(.*)", line)
        if not m:
            continue
        if m.group(1).startswith("cpu"):
            cpu_m = re.match("cpu(\d+)", m.group(1))
            if not cpu_m:
                tags = ''
                fields = m.group(2).split()
                cpu_types = [
                    'user', 'nice', 'system', 'idle', 'iowait',
                    'irq', 'softirq', 'guest', 'guest_nice'
                ]

                for value, field_name in zip(fields, cpu_types):
                    print "sys.stat.cpu %d %s type=%s%s" % (
                        ts, value, field_name, tags)
        elif m.group(1) == "intr":
            print (
                "sys.stat.intr %d %s"
                % (ts, m.group(2).split()[0]))
        elif m.group(1) == "ctxt":
            print "sys.stat.ctxt %d %s" % (ts, m.group(2))
        elif m.group(1) == "processes":
            print "sys.stat.processes %d %s" % (ts, m.group(2))
        elif m.group(1) == "procs_blocked":
            print "sys.stat.procs_blocked %d %s" % (ts, m.group(2))

    f_loadavg.seek(0)
    ts = int(time.time())
    for line in f_loadavg:
        m = re.match("(\S+)\s+(\S+)\s+(\S+)\s+(\d+)/(\d+)\s+", line)
        if not m:
            continue
        print "sys.loadavg.1min %d %s" % (ts, m.group(1))
        print "sys.loadavg.5min %d %s" % (ts, m.group(2))
        print "sys.loadavg.15min %d %s" % (ts, m.group(3))
        print "sys.loadavg.runnable %d %s" % (ts, m.group(4))
        print "sys.loadavg.total_threads %d %s" % (ts, m.group(5))

    f_entropy_avail.seek(0)
    ts = int(time.time())
    for line in f_entropy_avail:
        print "sys.kernel.entropy_avail %d %s" % (ts, line.strip())

    sys.stdout.flush()

if __name__ == "__main__":
    main()

