# -*- coding: utf-8 -*-

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


import signal
import multiprocessing
from multiprocessing import Process
from threading import Thread

from lib.dbus_handler_launcher import DBusHandlerLauncher
from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
import gui_updates
import tools

class Dispatch(Process):
    def __init__(self, events_out, updates_in, writers_in):
        Process.__init__(self)
        self.work = True
        self.events_out = events_out
        self.updates_in = updates_in
        self.writers_in = writers_in
        self.writing = None
        self.config = None

        self.drive_statuses = dict()
        self.drive_partitions = dict()

    def get_partitions_by_status(self, parent, status):
        if parent not in self.drive_partitions:
            return []
        return [
            part
            for part in self.drive_partitions[parent]
            if self.drive_partitions[parent][part] == status
        ]

    def parts_to_numbers(self, parent, parts):
        parts = [ str(tools.partnumber(parent, part)) for part in parts ]
        return ",".join( parts ) if len(parts) else "-"

    def __check_partitions(self, parent):
            awaited = self.get_partitions_by_status(parent, PartitionStatus.AWAITED)
            available = self.get_partitions_by_status(parent, PartitionStatus.AVAILABLE)
            in_progress = self.get_partitions_by_status(parent, PartitionStatus.IN_PROGRESS)
            done = self.get_partitions_by_status(parent, PartitionStatus.DONE)
            failed = self.get_partitions_by_status(parent, PartitionStatus.FAILED)

            if len(failed):
                return (DriveStatus.DRIVE_PARTERROR,
                        awaited,
                        available,
                        in_progress,
                        done,
                        failed
                       )

            if len(awaited):
                return (DriveStatus.DRIVE_HASPT,
                        awaited,
                        available,
                        in_progress,
                        done,
                        failed
                       )

            if len(available) or len(in_progress):
                return (DriveStatus.DRIVE_INPROGRESS,
                        awaited,
                        available,
                        in_progress,
                        done,
                        failed
                       )

            if \
                len(awaited) == 0 and \
                len(available) == 0 and \
                len(in_progress) == 0 and \
                len(done):
                    return (DriveStatus.DRIVE_DONE,
                            awaited,
                            available,
                            in_progress,
                            done,
                            failed
                           )

            return (DriveStatus.DRIVE_NEW,
                    awaited,
                    available,
                    in_progress,
                    done,
                    failed
                   )


    def update_status(self, parent, status_text):
        if parent not in self.drive_statuses:
            return

        drive_status = self.drive_statuses[parent]
        (parts_status, awaited, available, in_progress, done, failed) = \
            self.__check_partitions(parent)
        if not (drive_status & DriveStatus.DRIVE_PT):
            self.drive_statuses[parent] = parts_status

        drive_status = self.drive_statuses[parent]

        if drive_status == DriveStatus.DRIVE_PTERROR:
            drive_text = "Failed creating MBR."
        if drive_status == DriveStatus.DRIVE_WAITFORPT:
            drive_text = "Waiting for MBR..."

        if not (drive_status & DriveStatus.DRIVE_PT):
            failed_text = ""
            if failed:
                failed_text = "; failed: {0}".format(self.parts_to_numbers(parent, failed))
            drive_text = "{0} → {1} → {2} → {3}{4}".format(
                self.parts_to_numbers(parent, awaited),
                self.parts_to_numbers(parent, available),
                self.parts_to_numbers(parent, in_progress),
                self.parts_to_numbers(parent, done),
                failed_text
            )


        self.updates_in.put(
            gui_updates.StatusUpdate(
                parent,
                drive_status,
                drive_text
            )
        )

        if status_text is not None:
            self.updates_in.put(
                gui_updates.StatusBarUpdate(status_text)
            )
 

    def account_drive_added(self, drive):
        print(_("New drive: {0}").format(drive))
        if self.writing and self.config:
            self.drive_partitions[drive] = dict(
                (   [
                        "{0}{1}".format(drive, p),
                        PartitionStatus.AWAITED
                    ]
                    for p in self.config.partitions
                )
            )
            return True
        return False


    def account_partition_added(self, accepttype, parent, part):
        print(_("New partition: {0}").format(part))
        if part in self.drive_statuses:
            print("DRIVE STATUS (PADD): {0}".format(self.drive_statuses[self.path]))
        if    self.writing \
          and self.config \
          and parent in self.drive_statuses \
          and (accepttype is None or self.drive_statuses[parent] == accepttype):
            if part not in self.drive_partitions[parent]:
                self.drive_partitions[parent][part] = PartitionStatus.IGNORED
                return
            if self.drive_partitions[parent][part] == PartitionStatus.IGNORED:
                return
            self.drive_partitions[parent][part] = PartitionStatus.AVAILABLE
            awaited = \
                self.get_partitions_by_status(parent, PartitionStatus.AWAITED)

            return True if len(awaited) == 0 else False
        return False

        

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while self.work:
            order = self.events_out.get()
            order.handle(self)

        self.updates_in.close()
        self.updates_in.join_thread()
        self.writers_in.close()
        self.writers_in.join_thread()
        self.events_out.close()
        self.events_out.join_thread()
