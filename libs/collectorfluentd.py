#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: collectorfluentd.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-12-05 14:21:57
# @@Modify Date: 2013-12-06 18:12:37
# @@Function:
#*********************************************************#


import os
import time
import signal
import uuid
import glob
import msgpack_pure
import daemonize
from shelljob import proc
from common import log


class CollectorFluentd(object):
    """The main collector-fluentd class.

    There are 3 steps in a full running circle:

        1. getPluginsOutput, this function executes all plugins and gets
        there outputs lines as a list object. each item indicates a metric.

        2. write2Cache(outputs), write all metrics to local FS first.
        The content in cache files have already been msgpack encoded.

        3. sendAllCache, no param required.
        sendAllCache will search all cached files in cache folder, and send them
        to the remote fluentd server in order.
    """

    def __init__(self, conf):
        self.conf = conf
        log("Collector-fluentd daemon started, PID: %i" % daemonize.getPid())

    def _executePlugins(self, files):

        if not files: return []

        procs = []
        outputs = []

        # Running plugins parallel
        g = proc.Group()
        for f in files:
            procs.append(g.run(f))
            time.sleep(0.05)

        # Get lines
        t0 = time.time()
        while time.time() - t0 <= self.conf.plugin_timeout:
            if g.is_pending():
                _lines = g.readlines(max_lines=1)
                if _lines and _lines[0][1].strip():
                    outputs.append(_lines[0][1].strip())
            else:
                break

        # Clean up
        for p in procs:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except:
                pass

        return outputs

    def getPluginsOutput(self):
        log("Collecting metrics from plugins...", -1)
        log("Current plugin path: %s" % self.conf.plugin_path, -1)

        plugin_list = glob.glob(self.conf.plugin_path)
        plugin_list = [
            x for x in plugin_list if os.access(x, os.X_OK) and os.path.isfile(x)
        ]

        log("Found %i valid plugins: %s" % (
            len(plugin_list), str([os.path.basename(f) for f in plugin_list])), -1)
        
        log("Executing plugins...", -1)
        outputs = self._executePlugins(plugin_list)

        for output in outputs:
            log("Get valid plugin output: %s" % output.strip(), -1)

        return outputs

    def _getValidMetric(self, metric, addition={}):
        m = metric.split()

        if len(m) < 3:
            return False

        if not m[1].isdigit():
            return False

        try:
            v = float(m[2])
            if v == int(v):
                v = int(v)
        except:
            return False

        tags = {}
        for t in m[3:]:
            _t = t.split("=")
            if len(_t) != 2:
                return False
            if not _t[0].strip():
                return False
            if not _t[1].strip():
                return False
            tags[_t[0].strip()] = _t[1].strip()

        tags["_value"] = v

        if addition:
            for k in addition.keys():
                tags[k] = addition[k]

        log("Write validated metric %s to local FS..." % m[0], -1)
        return msgpack_pure.packs([m[0], int(m[1]), tags])

    def write2Cache(self, outputs):
        fname = "".join((
            self.conf.cache_path, "/",
            self.conf.cache_file_prefix,
            str(int(time.time())),
            "_",
            str(uuid.uuid1()),
            ".dat",
        ))
        log("Writting current metrics to local FS...", -1)
        log("Open cache file %s" % fname, -1)

        fcache = open(fname, "wb")
        for m in outputs:
            metric = self._getValidMetric(m, self.conf.tags)
            if metric:
                fcache.write(metric + '\n')
            else:
                log("Invalid metric string: %s (IGNORED)" % m, 1)
        fcache.close()

        if os.path.getsize(fname) == 0:
            log("No new metrics generated, removing current cache file.", 0)
            os.remove(fname)

    def logError(self, metric):
        err_msg = [" ".join((
            metric,
            str(int(time.time())),
            "1"
        ))]
        self.write2Cache(err_msg)


    def _getCachedMsg(self):

        fname = "".join((
            self.conf.cache_path, "/",
            self.conf.cache_file_prefix,
            "*.dat",
        ))
        cache_list = glob.glob(fname)
        cache_list.sort()
        if cache_list:
            return cache_list[0], open(cache_list[0], "rb").read()
        else:
            return None, None

    def sendAllCache(self, sock):
        log("Sending all cached message to remote server...", -1)
        while True:
            fname, msg = self._getCachedMsg()
            if fname:

                log("Sending cache file %s to server..." % os.path.basename(fname), -1)

                for _msg in msg.strip("\n").split("\n"):
                    if not sock.send(_msg):
                        self.logError("collector.error.send")
                        log("Could not connect to the fluentd server, metrics will be sent next time.", 2)
                        return False

                log("Successful sent metrics to server in cache file %s" % os.path.basename(fname), -1)
                os.remove(fname)
            else:
                break
        return True
