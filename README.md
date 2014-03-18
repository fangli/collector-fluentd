Collector-fluentd
=================

A distributed metric collection framework using fluentd protocol

-----------------

## Introduction

Collector-fluentd gathers metrics from varieties of plugins and send them to a fluentd server. Plugins are standard executable binaries or scripts which have metrics outputs in specific format.

## Usage

```
[root@my_host plugins]# collector-fluentd --help
usage: collector-fluentd -f [Configuration File Path]

optional arguments:
  -h, --help            show this help message and exit
  -f CONFIG, --config CONFIG
                        Path to configuration file, default to /etc/collector-
                        fluentd.conf
  -d, --daemonize       Run as a background daemon.
  -v, --version         Show version information of collector-fluentd.
```

## Configurations

**1. Section Main**

`pid_file` is the file which contains PID of running daemon

`plugin_path` points to the folder which contains plugins. Default to `[install path]/plugins` when leaving it empty

`log_file` points to a file in which collector-fluentd write logs

`log_level` is the logs level, optional values are `DEBUG`, `INFO`, `WARNING`, `CRITICAL`

`reporting_interval` is the most important config which decide the collecting interval, units of seconds

`plugin_timeout` decides the execution timeout when triggering a plugin. if a plugin didn't exit in specific time, it will be terminated by framework

`metric_prefix` is the global prefix. this value will be appended to metrics name automatically. For example, if the the output of a plugin is `mysql.connections 1395132494  863` and `metric_prefix=ops.` the real metric name sending to fluentd will be `ops.mysql.connections`

``

**2. Section Tags**

You could define your personality global tags here, for server recognizing.

Example:

```
[tags]
instanceid=i-xxxxxxx
area=asia
type=mysql
```

The tags in this section will be merged with the tags of plugins' output.

**3. Section Cache**

`cache_path` points to the cache file folder. when fluentd server is down, collector-fluentd will save metric data locally. **be sure you have created the folder manually!**

`cache_file_prefix` is the prefix of cache file name

**4. Section output**

`fluentd_host` is the remote fluentd server, Both hostname, FQDN and IP are acceptable.

`fluentd_port` is the remote port of fluentd instance

`connection_timeout` is the connection timeout between local and remote fluentd server.

## Plugins

Plugins are standard executable scripts. the output should like as below,

```
mysql.connections 1395132494 863
sys.load.5min 1395132494 3.2
net.send 1395132494 32847921 if=eth0
net.recv 1395132494 32847921 if=eth0
memcache.connections 1395132494 179 port=11211
...
```

One metric per line, tags are optional, blank space separated:

`[Metric.Name] [UNIX Timestamp] [Value] [k1=v1](optional) [k2=v2](optional)  ...`

**Be sure you have the plugin script executable permission** *(chmod +x my_plugin.sh)*

## Special Tags

`cf_datatype` is a special tag in collector-fluentd, it could be set to one of `GAUGE`(default), `COUNTER` and `DERIVE`, for values where you are interested in its value compared to the time

If you have a counter(like network traffic or mysql connection in total), you could use this special tag as below

```
net.send 1395132494 32847921 if=eth0 cf_datatype=counter
```

See [http://munin-monitoring.org/wiki/fieldname.type](http://munin-monitoring.org/wiki/fieldname.type) for details.

## Notes

Still in developing stage, use it at your own risk

## Releases

1.5.0: Add GAUGE, COUNTER and DERIVE data type support
