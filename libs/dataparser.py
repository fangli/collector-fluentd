#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: dataparser.py
# @@Author: Fang.Li<surivlee@gmail.com>
# @@Create Date: 2013-12-05 14:21:57
# @@Modify Date: 2014-03-13 18:07:34
# @@Function:
#*********************************************************#


import os


class Dataparser(object):

    def __init__(self, conf):
        self.conf = conf
        self.path = conf.cache_path + '/caches/'
        if not os.path.isdir(self.path):
            os.mkdir(conf.cache_path)
            os.mkdir(self.path)

    def __getHash(self, s):
        try: 
           from hashlib import md5
           m = md5(s)
           return m.hexdigest()
        except ImportError:
           import md5
           m = md5.new(s)
           return m.hexdigest()

    def __getPackHash(self, pack):
        ret = []
        ret.append(pack[0])
        for k in sorted(pack[2].keys()):
            if k != "_value":
                ret.append(k + pack[2][k])
        return self.__getHash("".join(ret))

    def getLastValue(self, pack):
        fname = self.__getPackHash(pack)
        if (os.path.isfile(self.path + fname)):
            f = open(self.path + fname, "r")
            fcontent = f.readlines()[0].split()
            f.close()
            return int(fcontent[0]), float(fcontent[1])
        else:
            return None, None

    def getCurrentValue(self, pack):
        return int(pack[1]), pack[2]['_value']

    def setValue(self, pack):
        fname = self.__getPackHash(pack)
        f = open(self.path + fname, "w")
        f.write(str(pack[1]) + ' ' + str(pack[2]['_value']))
        f.close()

    def gauge(self, pack):
        return pack

    def counter(self, pack):
        last_ts, last_v = self.getLastValue(pack)
        self.setValue(pack)
        if last_ts == None:
            return None
        else:
            current_ts, current_v = self.getCurrentValue(pack)
            if ((current_ts < last_ts) or (current_v < last_v)):
                return None
            else:
                pack[2]['_value'] = round((current_v - last_v) / (current_ts - last_ts), 2)
                return pack

    def derive(self, pack):
        last_ts, last_v = self.getLastValue(pack)
        self.setValue(pack)
        if last_ts == None:
            return None
        else:
            current_ts, current_v = self.getCurrentValue(pack)
            pack[2]['_value'] = round((current_v - last_v) / (current_ts - last_ts), 2)
            return pack

