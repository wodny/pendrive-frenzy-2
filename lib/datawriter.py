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
        # Creating MBR...
        self.events_in.put(StatusUpdate(
                                      self.drive,
                                      None,
                                      None,
                                      None,
                                      _("Creating MBR for {0}...".format(self.drive))
                                     ))


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


        # Adjusting partitions alignment...
        adjusted_specs = self.tools.adjust_partspecs_to_geometry(self.drive, self.request.partspecs)

        events = []

        for p in adjusted_specs:
            try:
                # Create partition (via MBR)
                part_path = self.tools.create_partition(self.drive, adjusted_specs[p])
                # Create FS (if specified)
                created = self.tools.create_fs(part_path, adjusted_specs[p])
                if created:
                    # FS created
                    events.append(FSCreated(self.drive, "{0}{1}".format(self.drive, p)))
                else:
                    # Partition for which mkfs is omitted
                    events.append(StatusUpdate(
                                               self.drive,
                                               None,
                                               part_path,
                                               PartitionStatus.DONE,
                                               _("Done {0}.".format(part_path))
                                 ))

            except dbus.DBusException, e:
                print(e)
                self.events_in.put(StatusUpdate(
                                              self.drive,
                                              DriveStatus.DRIVE_PTERROR,
                                              None,
                                              None,
                                              _("Error while creating partition {0} on {1}!".format(p, self.drive))
                                             ))
                return


        # Post-creation script
        if self.request.config.postscript:
            try:
                cmd = [self.request.config.postscript, self.tools.get_device_filename(self.drive)]
                print(cmd)
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError as e:
                print(e)
                self.events_in.put(StatusUpdate(
                                              self.drive,
                                              DriveStatus.DRIVE_PTERROR,
                                              None,
                                              None,
                                              _("Error executing postscript for {0}!".format(self.drive))
                                             ))
                return


        # Signal all partitions have been created
        for ev in events:
            self.events_in.put(ev)

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
        # Overall status
        success = True



        # Mount...
        if self.partspec["method"] == "copy-files":
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.IN_PROGRESS,
                                          _("Mounting {0}...".format(self.part))
                                         ))
            try:
                mountpoint = self.tools.mount(self.part)
            except dbus.DBusException:
                self.events_in.put(StatusUpdate(
                                              self.parent,
                                              None,
                                              self.part,
                                              PartitionStatus.FAILED,
                                              _("Error while mounting {0}!".format(self.part))
                                             ))
                return



        # Copying data...
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      None,
                                      self.part,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Copying to {0}...".format(self.part))
                                     ))

        try:
            cmd = []
            if self.partspec["method"] == "copy-files":
                cmd = ["rsync", "-rI", "--delete", "--", self.partspec["path"], mountpoint]
            if self.partspec["method"] == "copy-image":
                cmd = ["dd",
                       "bs=8M",
                       "if={0}".format(self.partspec["path"]),
                       "of={0}".format(self.tools.get_device_filename(self.part))
                      ]
            print(cmd)
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            # Continue for unmounting...
            success = False
            print(e)




        # Postcreation
        if self.partspec["method"] == "copy-files" and self.partspec["postscript"]:
            try:
                cmd = [self.partspec["postscript"], mountpoint]
                print(cmd)
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError as e:
                # Continue for unmounting...
                success = False
                print(e)


     


        # Unmounting...
        if self.partspec["method"] == "copy-files":
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.IN_PROGRESS,
                                          _("Unmounting {0}...".format(self.part))
                                         ))

            try:
                self.tools.unmount_retry(self.part)
            except dbus.DBusException:
                self.events_in.put(StatusUpdate(
                                              self.parent,
                                              None,
                                              self.part,
                                              PartitionStatus.FAILED,
                                              _("Error while unmounting {0}!".format(self.part))
                                             ))
                return



        # Report overall status
        if success:
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
