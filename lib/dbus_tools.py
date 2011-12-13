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
