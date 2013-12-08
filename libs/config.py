#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: config.py
# @@Author: Felix Lee <surivlee@gmail.com>
# @@Create Date: 11/18/2012
# @@Modify Date: 2013-12-08 17:39:13
# @@Function:
#*********************************************************#


__author__ = "Felix Lee <surivlee@gmail.com>"
__version__ = (0, 1)


import os
import __main__
import ConfigParser


LOG_LEVEL = "INFO"
LOG_FILE = "/var/log/collector-fluentd.log"


def readConfig(fname):
    global LOG_LEVEL
    global LOG_FILE

    _config_ = type('_', (object, ), dict())()

    config = ConfigParser.ConfigParser()
    config.read(fname)

    _config_.plugin_path = config.get("main", "plugin_path").strip().rstrip("/")
    _config_.log_level = config.get("main", "log_level").strip()
    _config_.log_file = config.get("main", "log_file").strip()
    _config_.pid_file = config.get("main", "pid_file").strip()
    _config_.metric_prefix = config.get("main", "metric_prefix").strip()
    _config_.reporting_interval = config.getint("main", "reporting_interval")
    _config_.plugin_timeout = config.getint("main", "plugin_timeout")

    _config_.cache_path = config.get("cache", "cache_path").strip().rstrip("/")
    _config_.cache_file_prefix = config.get("cache", "cache_file_prefix").strip()

    _config_.fluentd_host = config.get("output", "fluentd_host").strip()
    _config_.fluentd_port = config.getint("output", "fluentd_port")
    _config_.connection_timeout = config.getint("output", "connection_timeout")

    _config_.tags = {}
    for k in config.options("tags"):
        _config_.tags[k] = config.get("tags", k).strip()

    if _config_.plugin_path == "":
        _config_.plugin_path = os.path.dirname(
            os.path.realpath(__main__.__file__)
        ) + '/plugins/*'

    LOG_LEVEL = _config_.log_level
    LOG_FILE = _config_.log_file

    return _config_
