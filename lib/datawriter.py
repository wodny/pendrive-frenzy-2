# -*- coding: utf-8 -*-

#    Copyright 2011  Marcin Szewczyk <Marcin.Szewczyk@wodny.org>
#
#    This file is part of self.destination-frenzy.
#
#    self.destination-frenzy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    self.destination-frenzy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with self.destination-frenzy.  If not, see <http://www.gnu.org/licenses/>.


import subprocess
import time

from drive_statuses import DriveStatus
from datawriter_events import StatusUpdate
from dbus_tools import DBusTools

class DataWriter:
    def __init__(self, events_in, destination, source):
        self.destination = destination
        self.source = source
        self.events_in = events_in
        self.tools = DBusTools()
        self.parent = self.tools.get_parent(destination)

    def run(self):
        success = True

        #queue = EventQueue.instance()
        #dbus_handler = DBusHandler.instance()
        #self.destination = dbus_handler.get_parent(self.destination)

        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      self.destination,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Mounting...")
                                     ))
        try:
            #mountdestination = dbus_handler.mount(self.destination)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.destination,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while mounting!")
                                         ))
            return

        time.sleep(1)
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      self.destination,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Copying...")
                                     ))

        try:
            #subprocess.check_call(["rsync", "-rI", "--delete", "--", self.source, mountdestination])
            pass
        except subprocess.CalledProcessError as e:
            success = False
            print(e)
       
        time.sleep(1)
        # TODO: Anything less primitive?
        #time.sleep(3)
        self.events_in.put(StatusUpdate(
                                      self.parent,
                                      self.destination,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Unmounting...")
                                     ))

        time.sleep(1)
        try:
            #dbus_handler.unmount(self.destination)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.destination,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while unmounting!")
                                         ))
            return

        time.sleep(1)
        if success:
            # TODO: Anything less primitive?
            #time.sleep(3)
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.destination,
                                          DriveStatus.DRIVE_DONE,
                                          _("Done.")
                                         ))
        else:
            self.events_in.put(StatusUpdate(
                                          self.parent,
                                          self.destination,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while copying!")
                                         ))
