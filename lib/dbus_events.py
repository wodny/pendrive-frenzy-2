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
from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
from datawriter_requests import PartitionWriterRequest, MBRWriterRequest, FullDriveWriterRequest
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
                dispatch.drive_statuses[self.drive] = \
                    DriveStatus.DRIVE_WAITFORPT
                dispatch.writers_in.put(
                    MBRWriterRequest(
                        self.drive,
                        dispatch.config
                    )
                )
            elif dispatch.config.mode == "full-drive-image":
                dispatch.drive_statuses[self.drive] = \
                    DriveStatus.DRIVE_INPROGRESS_DRV
                dispatch.writers_in.put(
                    FullDriveWriterRequest(
                        self.drive,
                        dispatch.config
                    )
                )
            elif dispatch.config.mode == "copy-only":
                dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_NEW
        dispatch.updates_in.put(gui_updates.DriveAdded(self.drive, self.port))
        dispatch.update_status(self.drive, "New drive {0}.".format(self.drive))


class PartitionAdded(DBusEvent):
    def __init__(self, parent, part):
        self.parent = parent
        self.part = part

    def handle(self, dispatch):
        if dispatch.config and dispatch.config.mode in ("create-mbr", "full-drive-image"):
            return

        complete = dispatch.account_partition_added(
            (
                DriveStatus.DRIVE_NEW,
                DriveStatus.DRIVE_HASPT,
            ),
            self.parent,
            self.part
        )

        if complete:
            available = \
                dispatch.get_partitions_by_status(
                    self.parent,
                    PartitionStatus.AVAILABLE
                )
            for p in available:
                dispatch.drive_partitions[self.parent][p] = \
                    PartitionStatus.IN_PROGRESS
                partspec = \
                    dispatch.config.partspecs[tools.partnumber(self.parent, p)]
                dispatch.writers_in.put(
                    PartitionWriterRequest(self.parent, p, partspec)
                )

        dispatch.update_status(
            self.parent,
            "New partition {0}.".format(self.part)
        )


class DeviceRemoved(DBusEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        try:
            del dispatch.drive_partitions[self.path]
            del dispatch.drive_statuses[self.path]
        except KeyError:
            pass
        dispatch.updates_in.put(gui_updates.DeviceRemoved(self.path))
        # TODO: Do we need writer removal here?
