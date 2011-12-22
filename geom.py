#!/usr/bin/python

import lib.dbus_tools
import lib.config
import sys
import pprint
import time
import dbus

drive = "/org/freedesktop/UDisks/devices/sdd"

c = lib.config.Config(sys.argv[1])

t = lib.dbus_tools.DBusTools()
n = t.adjust_partspecs_to_geometry(drive, c.partspecs)
print("OLD")
pprint.pprint(c.partspecs)
print("NEW")
pprint.pprint(n)

for p in n:
    done = False
    tries = 0
    while not done:
        try:
            part = t.create_partition(drive, n[p])
            print(part)
            done = True
        except dbus.exceptions.DBusException, e:
            raise e
            #print(e)
            #tries += 1
            #if tries >= 5:
            #    raise e
            #time.sleep(3)

#t.create_fs("/org/freedesktop/UDisks/devices/sdd1", n[1])
