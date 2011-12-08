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
from datawriter_events import DataWriterRequest
from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus

class DBusEvent:
    pass

class DriveAdded(DBusEvent):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, dispatch):
        print(_("New drive: {0}").format(self.path))
        if dispatch.writing and dispatch.config:
            dispatch.drive_partitions[self.path] = dict(
                (   [
                        "{0}{1}".format(self.path, p),
                        PartitionStatus.AWAITED
                    ]
                    for p in dispatch.config.partitions
                )
            )
            if dispatch.config.mode == "create-mbr":
                dispatch.drive_statuses[self.path] = DriveStatus.DRIVE_WAITFORPT
                # PT Creation here
            else:
                dispatch.drive_statuses[self.path] = DriveStatus.DRIVE_NEW
        if self.path in dispatch.drive_statuses:
            print("DRIVE STATUS (ADD): {0}".format(dispatch.drive_statuses[self.path]))
        dispatch.updates_in.put(gui_updates.DriveAdded(self.path, self.port))
        dispatch.update_gui_status(self.path)


class PartitionAdded(DBusEvent):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, dispatch):
        print(_("New partition: {0}").format(self.path))
        if self.path in dispatch.drive_statuses:
            print("DRIVE STATUS (PADD): {0}".format(dispatch.drive_statuses[self.path]))
        if    dispatch.writing \
          and dispatch.config \
          and self.parent in dispatch.drive_statuses \
          and dispatch.drive_statuses[self.parent] == DriveStatus.DRIVE_NEW:
            if self.path not in dispatch.drive_partitions[self.parent]:
                dispatch.drive_partitions[self.parent][self.path] = PartitionStatus.IGNORED
                return
            if dispatch.drive_partitions[self.parent][self.path] == PartitionStatus.IGNORED:
                return
            dispatch.drive_partitions[self.parent][self.path] = PartitionStatus.AVAILABLE
            awaited = \
                dispatch.get_partitions_by_status(self.parent, PartitionStatus.AWAITED)

            if len(awaited) == 0:
                available = \
                    dispatch.get_partitions_by_status(self.parent, PartitionStatus.AVAILABLE)
                for part in available:
                    dispatch.drive_partitions[self.parent][part] = PartitionStatus.IN_PROGRESS
                    dispatch.writers_in.put(DataWriterRequest(part, "le source"))
            dispatch.update_gui_status(self.parent)

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
        dispatch.writers_in.put(DataWriterRequest(self.path, "le source", True))

class PartitionTableCreated(DBusEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        print(_("Partition table created: {0}").format(self.path))
        # TODO
        # PT
        # Set part. statuses as available/in progress
        dispatch.drive_statuses[self.path] = DriveStatus.DRIVE_PTDONE
        # FS creation here and worker right after that

class Dummy(DBusEvent):
    def __init__(self, text):
        self.text = text

    def handle(self, dispatch):
        print("TEXT: {0}".format(self.text))
