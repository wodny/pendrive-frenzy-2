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


import subprocess
import time

from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
from datawriter_events import StatusUpdate
from dbus_tools import DBusTools
from dbus_virtevents import MBRCreated, PartitionsCreated, FSCreated

import dbus
import logging

class MBRWriter:
    def __init__(self, events_in, request):
        self.events_in = events_in
        self.request = request

        self.drive = request.drive
        self.tools = DBusTools()

    def run(self):
        # Creating MBR...
        logging.info(_("Creating MBR for {0}...").format(self.drive))
        self.events_in.put(StatusUpdate(
                                      self.drive,
                                      None,
                                      None,
                                      None,
                                      _("Creating MBR for {0}...").format(self.drive)
                                     ))


        try:
            device = self.tools.get_device(self.drive)
            self.tools.create_mbr(self.drive)

        except dbus.DBusException:
            logging.error(_("Error while creating MBR on {0}!").format(self.drive))
            self.events_in.put(StatusUpdate(
                                          self.drive,
                                          DriveStatus.DRIVE_PTERROR,
                                          None,
                                          None,
                                          _("Error while creating MBR on {0}!").format(self.drive)
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
                    logging.info(_("Filesystem created on {0}").format(part_path))
                    events.append(FSCreated(self.drive, "{0}{1}".format(self.drive, p)))
                else:
                    logging.info(_("Partition {0} done.").format(part_path))
                    # Partition for which mkfs is omitted
                    events.append(StatusUpdate(
                                               self.drive,
                                               None,
                                               part_path,
                                               PartitionStatus.DONE,
                                               _("Partition {0} done.").format(part_path)
                                 ))

            except dbus.DBusException, e:
                logging.error(_("Error while creating partition {0} on {1}: {2}").format(p, self.drive, e))
                self.events_in.put(StatusUpdate(
                                              self.drive,
                                              DriveStatus.DRIVE_PTERROR,
                                              None,
                                              None,
                                              _("Error while creating partition {0} on {1}!").format(p, self.drive)
                                             ))
                return


        # Post-creation script
        if self.request.config.postscript:
            try:
                cmd = [self.request.config.postscript, self.tools.get_device_filename(self.drive)]
                logging.debug(_("Executing post-MBR script {0}...").format(cmd))
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError as e:
                logging.error(_("Error executing postscript for {0}: {1}!").format(self.drive, e))
                self.events_in.put(StatusUpdate(
                                              self.drive,
                                              DriveStatus.DRIVE_PTERROR,
                                              None,
                                              None,
                                              _("Error executing postscript for {0}!").format(self.drive)
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
            logging.info(_("Mounting {0}...").format(self.part))
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.IN_PROGRESS,
                                          _("Mounting {0}...").format(self.part)
                                         ))
            try:
                mountpoint = self.tools.mount(self.part)
            except dbus.DBusException, e:
                logging.error(_("Error while mounting {0}: {1}").format(self.part, e))
                self.events_in.put(StatusUpdate(
                                              self.parent,
                                              None,
                                              self.part,
                                              PartitionStatus.FAILED,
                                              _("Error while mounting {0}!").format(self.part)
                                             ))
                return



        # Copying data...
        logging.info(_("Copying to {0}...").format(self.part))
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      None,
                                      self.part,
                                      PartitionStatus.IN_PROGRESS,
                                      _("Copying to {0}...").format(self.part)
                                     ))

        try:
            cmd = []
            if self.partspec["method"] == "copy-files":
                cmd = ["rsync", "-rI", "--delete", "--", self.partspec["path"], mountpoint]
            if self.partspec["method"] == "copy-image":
                cmd = ["dd",
                       "bs=8M",
                       "conv=fsync",
                       "if={0}".format(self.partspec["path"]),
                       "of={0}".format(self.tools.get_device_filename(self.part))
                      ]
            logging.debug(_("Executing copy command {0}...").format(cmd))
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            for line in output.split('\n'):
                logging.debug(_("Command output: {0}").format(line))
        except subprocess.CalledProcessError as e:
            # Continue for unmounting...
            logging.error(_("Error executing copy command: {0}").format(e))
            success = False




        # Postcreation
        if self.partspec["method"] == "copy-files" and self.partspec["postscript"]:
            try:
                cmd = [self.partspec["postscript"], mountpoint]
                logging.debug(_("Executing post-partition script {0}...").format(cmd))
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError as e:
                # Continue for unmounting...
                logging.error(_("Error executing postscript: {0}").format(e))
                success = False


     


        # Unmounting...
        if self.partspec["method"] == "copy-files":
            logging.info(_("Unmounting {0}...").format(self.part))
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.IN_PROGRESS,
                                          _("Unmounting {0}...").format(self.part)
                                         ))

            try:
                self.tools.unmount_retry(self.part)
            except dbus.DBusException:
                logging.error(_("Error while unmounting {0}!").format(self.part))
                self.events_in.put(StatusUpdate(
                                              self.parent,
                                              None,
                                              self.part,
                                              PartitionStatus.FAILED,
                                              _("Error while unmounting {0}!").format(self.part)
                                             ))
                return



        # Report overall status
        if success:
            logging.info(_("Partition {0} done.").format(self.part))
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.DONE,
                                          _("Partition {0} done.").format(self.part)
                                         ))
        else:
            logging.error(_("Error while copying {0}!").format(self.part))
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          None,
                                          self.part,
                                          PartitionStatus.FAILED,
                                          _("Error while copying {0}!").format(self.part)
                                         ))
