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

class DBusHandler:
    def __init__(self, events_out):
        self.events_out = events_out

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

    def handler(self, *args, **kwargs):
        member = kwargs['member']
        path = args[0]
        print("{0} - {1}".format(member, path))
        #self.tools.get_conn_interface(path) == "usb":
        if member == "DeviceAdded" and \
           self.tools.is_drive(path)     :#and \
            port = self.tools.get_port(path)
            self.events_out.send(DriveAdded(path, port))
        if member == "DeviceAdded" and self.tools.is_partition(path):
            self.events_out.send(PartitionAdded(path, self.get_parent(path)))
        if member == "DeviceRemoved":
            self.events_out.send(DeviceRemoved(path))
