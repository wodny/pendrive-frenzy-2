#!/usr/bin/python

import lib.dbus_tools
import lib.tools
import sys


if len(sys.argv) < 2:
    exit("Device filename is required (eg. /dev/sdd).")

parentdev = sys.argv[1]

t = lib.dbus_tools.DBusTools()
parentpath = t.get_path_of_devfile(parentdev)
children = t.get_children(parentpath)

print("[general]")
print("; Uncomment the chosen mode")
print(";mode = copy-only")
print(";mode = create-mbr")

parts = ','.join(
    [str(lib.tools.partnumber(parentpath, child)) for child in children]
)
print("partitions = {0}".format(parts))
print("description = An example")
print("copycommand =")
print("copycommand_params =")
print("postscript =")
print("")

for child in children:
    (start, size, ptype, fstype, label, boot) = t.get_partition_spec(child)
    partnumber = lib.tools.partnumber(parentpath, child)
    print("[partition_{0}]".format(partnumber))
    print("start = {0}".format(start))
    print("size = {0}".format(size))
    print("type = {0}".format(ptype))
    print("fstype = {0}".format(fstype))
    print("label = {0}".format(label))
    print("boot = {0}".format(boot))
    print("postscript =")
    print("")
