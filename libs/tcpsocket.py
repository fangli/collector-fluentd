#!/usr/bin/env python
# -*- coding:utf-8 -*-

#*********************************************************#
# @@ScriptName: tcpsocket.py
# @@Author: Felix Lee <surivlee@gmail.com>
# @@Create Date: 11/18/2012
# @@Modify Date: 2013-12-06 12:51:09
# @@Function:
#*********************************************************#


__author__ = "Felix Lee <surivlee@gmail.com>"
__version__ = (0, 1)


import socket


class TcpSocket(object):
    """TCP sockect with auto reconnect.

    THe implementation of following class is inspired from 
    https://github.com/yosisa/pyfluent/blob/master/pyfluent/client.py
    Thanks to yosisa's work
    """

    def __init__(self, host="localhost", port=24224, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock = None

    def _persist_socket(self):
        if not self._sock:
            self._create_socket()
        return self._sock

    def _make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock

    def _create_socket(self):
        try:
            self._sock = self._make_socket()
        except:
            pass

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except:
                pass
            self._sock = None

    def send(self, msg):
        sock = self._persist_socket()
        try:
            sock.sendall(msg)
            return True
        except:
            self.close()
            return False
