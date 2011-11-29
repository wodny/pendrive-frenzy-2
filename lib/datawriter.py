# -*- coding: utf-8 -*-

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

        self.events_in.send(StatusUpdate(
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Mounting...")
                                     ))
        try:
            #mountdestination = dbus_handler.mount(self.destination)
            pass
        except dbus.DBusException:
            self.events_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while mounting!")
                                         ))
            return

        time.sleep(1)
        self.events_in.send(StatusUpdate(
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
        self.events_in.send(StatusUpdate(
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Unmounting...")
                                     ))

        time.sleep(1)
        try:
            #dbus_handler.unmount(self.destination)
            pass
        except dbus.DBusException:
            self.events_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while unmounting!")
                                         ))
            return

        time.sleep(1)
        if success:
            # TODO: Anything less primitive?
            #time.sleep(3)
            self.events_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_DONE,
                                          _("Done.")
                                         ))
        else:
            self.events_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while copying!")
                                         ))
