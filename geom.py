#!/usr/bin/python

import lib.dbus_tools
import lib.config
import sys
import pprint

drive = "/org/freedesktop/UDisks/devices/sdd"

c = lib.config.Config(sys.argv[1])

t = lib.dbus_tools.DBusTools()
n = t.adjust_partspecs_to_geometry(drive, c.partspecs)
print("OLD")
pprint.pprint(c.partspecs)
print("NEW")
pprint.pprint(n)

for p in n:
    prev_start = t.create_partition(drive, n[p])
