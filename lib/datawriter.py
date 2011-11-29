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
from datawriter_events import StatusUpdate

class DataWriter:
    def __init__(self, events_in, destination, source):
        self.destination = destination
        self.source = source
        self.events_in = events_in

    def run(self):
        success = True
        #queue = EventQueue.instance()
        #dbus_handler = DBusHandler.instance()
        #pendrive = dbus_handler.get_parent(self.destination)
        pendrive = self.destination

        self.events_in.put(StatusUpdate(
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Mounting...")
                                     ))
        try:
            #mountdestination = dbus_handler.mount(self.destination)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while mounting!")
                                         ))
            return

        time.sleep(1)
        self.events_in.put(StatusUpdate(
                                      pendrive,
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
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Unmounting...")
                                     ))

        time.sleep(1)
        try:
            #dbus_handler.unmount(self.destination)
            pass
        except dbus.DBusException:
            self.events_in.put(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while unmounting!")
                                         ))
            return

        time.sleep(1)
        if success:
            # TODO: Anything less primitive?
            #time.sleep(3)
            self.events_in.put(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_DONE,
                                          _("Done.")
                                         ))
        else:
            self.events_in.put(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while copying!")
                                         ))

        self.events_in.close()
        self.events_in.join_thread()
