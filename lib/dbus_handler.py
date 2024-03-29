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
from dbus.mainloop.glib import DBusGMainLoop
from dbus_events import *
from dbus_tools import DBusTools
import logging


class DBusHandler:
    def __init__(self, events_in):
        self.events_in = events_in

        DBusGMainLoop(set_as_default=True)

        self.systembus = dbus.SystemBus()
        self.systembus.add_signal_receiver(self.handler,
                                     dbus_interface="org.freedesktop.UDisks",
                                     path="/org/freedesktop/UDisks",
                                     sender_keyword="sender",
                                     destination_keyword="dest",
                                     interface_keyword="iface",
                                     member_keyword="member",
                                     path_keyword="path"
                                    )

        # Assure the UDisks service runs
        self.tools = DBusTools()
        self.tools.get_device("/org/freedesktop/UDisks")

        self.drives = dict()

    def handler(self, *args, **kwargs):
        member = kwargs['member']

        if len(args) >= 1:
            path = args[0]
        else:
            return

        if member == "DeviceAdded" and \
           self.tools.is_drive(path) and \
           self.tools.get_conn_interface(path) == "usb":
            driveid = self.tools.get_drive_id(path)
            port = self.tools.get_port(path)
            size = self.tools.get_device_size(path)
            logging.info(_("New drive {0} {1} (size={2}).").format(path, driveid, size))
            if size != 0:
                self.events_in.put(DriveAdded(path, port))
            self.drives[path] = size

        if member == "DeviceChanged" and \
           self.tools.is_drive(path) and \
           self.tools.get_conn_interface(path) == "usb":
            driveid = self.tools.get_drive_id(path)
            port = self.tools.get_port(path)
            size = self.tools.get_device_size(path)
            logging.info(_("Drive {0} {1} changed (size={2}).").format(path, driveid, size))
            if path in self.drives and self.drives[path] == 0 and size != 0:
                self.events_in.put(DriveAdded(path, port))
            if path in self.drives and size == 0:
                self.events_in.put(DeviceRemoved(path))
            self.drives[path] = size

        if member == "DeviceAdded" and self.tools.is_partition(path):
            logging.debug(_("New partition {0}.").format(path))
            self.events_in.put(
                PartitionAdded(
                    self.tools.get_parent(path),
                    path
                )
            )
        if member == "DeviceRemoved":
            logging.debug(_("Removed device {0}.").format(path))
            try:
                del self.drives[path]
            except KeyError:
                pass
            self.events_in.put(DeviceRemoved(path))
