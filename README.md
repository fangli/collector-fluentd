Collector-fluentd
====================

Collector-fluentd is a large-scale system metric collecting tool for fluentd

Notes
--------

Still in developing stage, use it at your own risk

Releases
--------

We have launched the first alpha release, it's not for production use.
Everything work well except losing data sometimes.


Usage
---------

usage: collector-fluentd -f [Configuration File Path]

optional arguments:
  -h, --help            show this help message and exit
  -f CONFIG, --config CONFIG
                        Path to configuration file, default to /etc/collector-
                        fluentd.conf
  -d, --daemonize       Run as a background daemon.