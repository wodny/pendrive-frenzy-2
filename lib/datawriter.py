# -*- coding: utf-8 -*-

#    Copyright 2011  Marcin Szewczyk <Marcin.Szewczyk@wodny.org>
#
#    This file is part of self.partition-frenzy.
#
#    self.partition-frenzy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    self.partition-frenzy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with self.partition-frenzy.  If not, see <http://www.gnu.org/licenses/>.


import subprocess
import time

from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
from datawriter_events import StatusUpdate
from dbus_tools import DBusTools
from dbus_virtevents import MBRCreated, PartitionsCreated, FSCreated

import dbus
import random

class MBRWriter:
    def __init__(self, events_in, request):
        self.events_in = events_in
        self.request = request

        self.drive = request.drive
        self.tools = DBusTools()

    def run(self):

        #time.sleep(1)

        self.events_in.put(StatusUpdate(
                                      self.drive,
                                      None,
                                      None,
                                      None,
                                      _("Creating MBR for {0}...".format(self.drive))
                                     ))

        #time.sleep(1)

        try:
            device = self.tools.get_device(self.drive)
            self.tools.create_mbr(self.drive)

        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.drive,
                                          DriveStatus.DRIVE_PTERROR,
                                          None,
                                          None,
                                          _("Error while creating MBR on {0}!".format(self.drive))
                                         ))
            return

        self.events_in.put(MBRCreated(self.drive))

        #time.sleep(1)

        prev_start = 0
        for p in self.request.partspecs:
            prev_start = self.tools.create_partition(self.drive, self.request.partspecs[p], prev_start)
            self.events_in.put(FSCreated(self.drive, "{0}{1}".format(self.drive, p)))


        return PartitionsCreated(self.drive)




class PartitionWriter:
    def __init__(self, events_in, request):
        self.events_in = events_in
        self.request = request

        self.parent = request.parent
        self.part = request.part
        self.partspec = request.partspec

        self.tools = DBusTools()

    def run(self):
        random.seed()
        success = True

        #queue = EventQueue.instance()
        #dbus_handler = DBusHandler.instance()
        #self.part = dbus_handler.get_parent(self.part)

        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      None,
                                      self.part,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Mounting {0}...".format(self.part))
                                     ))
        try:
            #mountpartition = dbus_handler.mount(self.part)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.FAILED,
                                          _("Error while mounting {0}!".format(self.part))
                                         ))
            return

        time.sleep(random.randint(1,5))
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      None,
                                      self.part,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Copying to {0}...".format(self.part))
                                     ))

        try:
            #subprocess.check_call(["rsync", "-rI", "--delete", "--", self.source, mountpartition])
            pass
        except subprocess.CalledProcessError as e:
            success = False
            print(e)
       
        time.sleep(random.randint(1,5))
        # TODO: Anything less primitive?
        #time.sleep(random.randint(1,5))
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      None,
                                      self.part,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Unmounting {0}...".format(self.part))
                                     ))

        time.sleep(random.randint(1,5))
        try:
            #dbus_handler.unmount(self.part)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.FAILED,
                                          _("Error while unmounting {0}!".format(self.part))
                                         ))
            return

        time.sleep(random.randint(1,5))
        if success:
            # TODO: Anything less primitive?
            #time.sleep(random.randint(1,5))
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.DONE,
                                          _("Done {0}.".format(self.part))
                                         ))
        else:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.FAILED,
                                          _("Error while copying {0}!".format(self.part))
                                         ))

        if random.randint(1,3) < 2:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.FAILED,
                                          _("Error while copying {0}!".format(self.part))
                                         ))


