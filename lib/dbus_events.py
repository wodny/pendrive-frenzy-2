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



import gui_updates
from datawriter_removal import DataWriterRemoval
from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
from dbus_tools import DBusTools
from datawriter_requests import PartitionWriterRequest, MBRWriterRequest
import tools

class DBusEvent:
    pass

class DriveAdded(DBusEvent):
    def __init__(self, drive, port):
        self.drive = drive
        self.port = port

    def handle(self, dispatch):
        added = dispatch.account_drive_added(self.drive)
        if added:
            if dispatch.config.mode == "create-mbr":
                dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_WAITFORPT
                dispatch.writers_in.put(MBRWriterRequest(self.drive, dispatch.config.partspecs))
            else:
                dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_NEW
        if self.drive in dispatch.drive_statuses:
            print("DRIVE STATUS (ADD): {0}".format(dispatch.drive_statuses[self.drive]))
        dispatch.updates_in.put(gui_updates.DriveAdded(self.drive, self.port))
        dispatch.update_status(self.drive, "New drive {0}.".format(self.drive))



class PartitionAdded(DBusEvent):
    def __init__(self, parent, part):
        self.parent = parent
        self.part = part

    def handle(self, dispatch):
        complete = dispatch.account_partition_added(DriveStatus.DRIVE_NEW, self.parent, self.part)
        if complete:
            available = \
                dispatch.get_partitions_by_status(self.parent, PartitionStatus.AVAILABLE)
            for p in available:
                dispatch.drive_partitions[self.parent][p] = PartitionStatus.IN_PROGRESS
                partspec = dispatch.config.partspecs[tools.partnumber(self.parent, p)]
                dispatch.writers_in.put(PartitionWriterRequest(self.parent, p, partspec))
        dispatch.update_status(self.parent, "New partition {0}.".format(self.part))


class DeviceRemoved(DBusEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        print(_("Device removed: {0}").format(self.path))
        if self.path in dispatch.drive_statuses:
            print("DRIVE STATUS (RM): {0}".format(dispatch.drive_statuses[self.path]))
        try:
            del dispatch.drive_partitions[self.path]
            del dispatch.drive_statuses[self.path]
        except KeyError:
            pass
        dispatch.updates_in.put(gui_updates.DeviceRemoved(self.path))
        # TODO: reenable
        #dispatch.writers_in.put(DataWriterRequest(self.path, "le source", True))

class Dummy(DBusEvent):
    def __init__(self, text):
        self.text = text

    def handle(self, dispatch):
        print("TEXT: {0}".format(self.text))
