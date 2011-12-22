#    Copyright 2011  Marcin Szewczyk <Marcin.Szewczyk@wodny.org>
#
#    This file is part of pendrive-frenzy.
#
#    Pendrive-frenzy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pendrive-frenzy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pendrive-frenzy.  If not, see <http://www.gnu.org/licenses/>.


import dbus
import parted
import copy
import math

class DBusTools:
    def __init__(self):
        self.systembus = dbus.SystemBus()

    def get_device(self, path):
        return self.systembus.get_object(
                                         'org.freedesktop.UDisks',
                                         path
                                        )

    def get_prop(self, device, propname):
        return device.Get(
                          'org.freedesktop.UDisks.Device',
                          propname,
                          dbus_interface = 'org.freedesktop.DBus.Properties',
                          timeout = 300
                         )

    def is_drive(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DeviceIsDrive")

    def is_partition(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DeviceIsPartition")

    def get_port(self, path):
        device = self.get_device(path)
        port = self.get_prop(device, "NativePath")
        return port[port.find("/usb"): port.rfind("/host")]

    def get_parent(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "PartitionSlave")

    def mount(self, path):
        device = self.get_device(path)
        if self.get_prop(device, "DeviceIsMounted"):
            return self.get_prop(device, "DeviceMountPaths")[0]
        return device.FilesystemMount(
                                      "", [],
                                      dbus_interface = 'org.freedesktop.UDisks.Device',
                                      timeout = 300
                                     )

    def unmount(self, path):
        device = self.get_device(path)
        return device.FilesystemUnmount(
                                        [],
                                        dbus_interface = 'org.freedesktop.UDisks.Device',
                                        timeout = 300
                                       )

    def create_mbr(self, path):
        device = self.get_device(path)
        device.PartitionTableCreate("mbr", [], dbus_interface = 'org.freedesktop.UDisks.Device')

    def get_conn_interface(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DriveConnectionInterface")

    def get_device_size(self, path):
        device = self.get_device(path)
        return int(self.get_prop(device, "DeviceSize"))

    def floor_to_chunk(self, size, chunksize):
        return size - size % chunksize

    def ceil_to_chunk(self, size, chunksize):
        return int(math.ceil(1.0 * size / chunksize) * chunksize)
   
    def get_geometry(self, path):
        devfile = self.get_device_filename(path)
        pdevice = parted.device.Device(devfile)
        return pdevice.hardwareGeometry + ( pdevice.physicalSectorSize, )

    def get_chunk_size(self, path):
        (cylinders, heads, sectors, sectorsize) = self.get_geometry(path)
        return heads * sectors * sectorsize

    def get_device_filename(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DeviceFile")

    def adjust_partspecs_to_geometry(self, drive, partspecs):
        chunksize = self.get_chunk_size(drive)
        newspecs = copy.deepcopy(partspecs)

        devsize = self.get_device_size(drive) 
        maxend = self.floor_to_chunk(devsize - 10 * chunksize, chunksize)

        (cylinders, heads, sectors, sectorsize) = self.get_geometry(drive)
        first_free = 1 * sectors

        for i in newspecs:
            part = newspecs[i]
            start = part["start"]
            start = self.floor_to_chunk(start, chunksize)
            if start < first_free:
                start = first_free

            end = start + part["size"]
            end = self.ceil_to_chunk(end, chunksize)
            if end > maxend:
                end = maxend

            size = end - start

            part["start"] = start
            part["size"] = size

            if int(part["type"], 16) == 0x05:
                first_free = start + sectors * 512
            else:
                first_free = start + size

        extended = None
        lastpartend = None
        for i in newspecs.keys():
            part = newspecs[i]
            if int(part["type"], 16) == 0x05:
                if extended is None:
                    extended = part
                else:
                    del newspecs[i]
                continue
            if extended is None:
                continue
            lastpartend = part["start"] + part["size"]

        if extended is not None and lastpartend is not None:
            extended["size"] = lastpartend - extended["start"]

        return newspecs

    def create_partition(self, drive, partspec):
        chunk_size = self.get_chunk_size(drive)
        start = partspec["start"]
        size = partspec["size"]
        flags = ["boot"] if partspec["boot"] else []

        device = self.get_device(drive)

        print("Bytes  : {0} -- {1}  ({2})".format(start, (start + size - 1), size))
        print("Sectors: {0} -- {1}  ({2})".format(start / 512, (start + size - 1) / 512, size / 512))

        #return
        partition = device.PartitionCreate(
                                           start,
                                           size,
                                           partspec["type"],
                                           "",
                                           flags,
                                           [],
                                           "",
                                           [],
                                           dbus_interface = 'org.freedesktop.UDisks.Device',
                                           timeout = 300
                                          )
        return partition

    def create_fs(self, device, partspec):
        options = ["label={0}".format(partspec["label"])] if len(partspec["label"]) else []
        device = self.get_device(device)

        print("FS")

        partition = device.FilesystemCreate(
                                           partspec["fstype"],
                                           options,
                                           dbus_interface = 'org.freedesktop.UDisks.Device',
                                           timeout = 300
                                          )

