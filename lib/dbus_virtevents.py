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




# Because currently UDisks' DeviceJobChanged is not very useful, this 
# wrapper is used.

from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
import tools
from datawriter_requests import PartitionWriterRequest

class DBusVirtEvent:
    pass

class MBRCreated(DBusVirtEvent):
    def __init__(self, drive):
        self.drive = drive

    def handle(self, dispatch):
        print(_("MBR created: {0}").format(self.drive))
        dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_HASPT
        dispatch.update_status(self.drive, "New MBR for {0}.".format(self.drive))

class PartitionsCreated(DBusVirtEvent):
    def __init__(self, drive):
        self.drive = drive

    def handle(self, dispatch):
        print(_("Partitions created: {0}").format(self.drive))
        dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_HASPT
        dispatch.update_status(self.drive, "Created partitions on {0}.".format(self.drive))

class FSCreated(DBusVirtEvent):
    def __init__(self, drive, part):
        self.drive = drive
        self.part = part

    def handle(self, dispatch):
        print("Filesystem created on {0}.".format(self.part))

        dispatch.account_partition_added(None, self.drive, self.part)
        dispatch.drive_partitions[self.drive][self.part] = PartitionStatus.AVAILABLE
        dispatch.update_status(self.drive, "New partition {0}.".format(self.part))

        partspec = dispatch.config.partspecs[tools.partnumber(self.drive, self.part)]
        dispatch.writers_in.put(PartitionWriterRequest(self.drive, self.part, partspec))
