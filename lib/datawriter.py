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

from partition_statuses import PartitionStatus
from datawriter_events import StatusUpdate
from dbus_tools import DBusTools

import random

class DataWriter:
    def __init__(self, events_in, partition, source):
        self.partition = partition
        self.source = source
        self.events_in = events_in
        self.tools = DBusTools()
        self.parent = self.tools.get_parent(partition)

    def run(self):
        random.seed()
        success = True

        #queue = EventQueue.instance()
        #dbus_handler = DBusHandler.instance()
        #self.partition = dbus_handler.get_parent(self.partition)

        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      self.partition,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Mounting {0}...".format(self.partition))
                                     ))
        try:
            #mountpartition = dbus_handler.mount(self.partition)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.partition,
                                          PartitionStatus.FAILED,
                                          _("Error while mounting {0}!".format(self.partition))
                                         ))
            return

        time.sleep(random.randint(1,5))
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      self.partition,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Copying to {0}...".format(self.partition))
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
                                      self.partition,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Unmounting {0}...".format(self.partition))
                                     ))

        time.sleep(random.randint(1,5))
        try:
            #dbus_handler.unmount(self.partition)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.partition,
                                          PartitionStatus.FAILED,
                                          _("Error while unmounting {0}!".format(self.partition))
                                         ))
            return

        time.sleep(random.randint(1,5))
        if success:
            # TODO: Anything less primitive?
            #time.sleep(random.randint(1,5))
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.partition,
                                          PartitionStatus.DONE,
                                          _("Done {0}.".format(self.partition))
                                         ))
        else:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.partition,
                                          PartitionStatus.FAILED,
                                          _("Error while copying {0}!".format(self.partition))
                                         ))

        if random.randint(1,3) < 2:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.partition,
                                          PartitionStatus.FAILED,
                                          _("Error while copying {0}!".format(self.partition))
                                         ))


