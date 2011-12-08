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
        parts = [ part[len(parent):] for part in parts ]
        return ",".join( parts ) if len(parts) else "-"

    def update_gui_status(self, parent):
        awaited = self.get_partitions_by_status(parent, PartitionStatus.AWAITED)
        available = self.get_partitions_by_status(parent, PartitionStatus.AVAILABLE)
        in_progress = self.get_partitions_by_status(parent, PartitionStatus.IN_PROGRESS)
        done = self.get_partitions_by_status(parent, PartitionStatus.DONE)
        failed = self.get_partitions_by_status(parent, PartitionStatus.FAILED)

        summary = "{0} → {1} → {2} → {3}; failed: {4}".format(
            self.parts_to_numbers(parent, awaited),
            self.parts_to_numbers(parent, available),
            self.parts_to_numbers(parent, in_progress),
            self.parts_to_numbers(parent, done),
            self.parts_to_numbers(parent, failed)
        )

        drive_status = DriveStatus.DRIVE_NEW
        if len(awaited):
            drive_status = DriveStatus.DRIVE_SELECTED
        if len(available) or len(in_progress):
            drive_status = DriveStatus.DRIVE_INPROGRESS 
        if \
            len(awaited) == 0 and \
            len(available) == 0 and \
            len(in_progress) == 0 and \
            len(done):
                drive_status = DriveStatus.DRIVE_DONE 
        if len(failed):
            drive_status = DriveStatus.DRIVE_ERROR

        self.updates_in.put(
            gui_updates.StatusUpdate(
                parent,
                drive_status,
                summary
            )
        )


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
