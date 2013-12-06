#!/usr/bin/env python
# -*- coding:utf-8 -*-

# *********************************************************#
# @@ScriptName: nginx.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-07-10 11:02:09
# @@Modify Date: 2013-12-06 11:46:42
# @@Function:
# *********************************************************#


import time
import urllib2
import re


NGINX_STATUS_URL = "http://localhost/nginx_status"


def printStats(metric, ts, value):
    if value is not None:
        print "nginx.%s %i %s" % (metric.lower(), int(ts), str(value))


def get_data(url):
    data = urllib2.urlopen(url)
    data = data.read()
    result = {}

    match1 = re.search(r'Active connections:\s+(\d+)', data)
    match2 = re.search(r'\s*(\d+)\s+(\d+)\s+(\d+)', data)
    match3 = re.search(r'Reading:\s*(\d+)\s*Writing:\s*(\d+)\s*'
                       'Waiting:\s*(\d+)', data)
    if not match1 or not match2 or not match3:
        raise Exception('Unable to parse %s' % url)

    result['connections'] = int(match1.group(1))

    result['accepted'] = int(match2.group(1))
    result['handled'] = int(match2.group(2))
    result['requests'] = int(match2.group(3))

    result['reading'] = int(match3.group(1))
    result['writing'] = int(match3.group(2))
    result['waiting'] = int(match3.group(3))

    return result


def main():
    ts = time.time()
    status = get_data(NGINX_STATUS_URL)
    for k, v in status.iteritems():
        printStats(k, ts, v)


if __name__ == "__main__":
    main()
