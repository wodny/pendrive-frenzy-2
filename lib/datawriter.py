# -*- coding: utf-8 -*-

import subprocess
from threading import Thread
import time

from drive_statuses import DriveStatus
from writer_events import StatusUpdate

class DataWriter(Thread):
    def __init__(self, updates_in, path, source):
        Thread.__init__(self)
        self.path = path
        self.source = source
        self.updates_in = updates_in

    def run(self):
        success = True
        #queue = EventQueue.instance()
        #dbus_handler = DBusHandler.instance()
        #pendrive = dbus_handler.get_parent(self.path)
        pendrive = "Le pendrive"

        self.updates_in.send(StatusUpdate(
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Mounting...")
                                     ))
        try:
            #mountpath = dbus_handler.mount(self.path)
            pass
        except dbus.DBusException:
            self.updates_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while mounting!")
                                         ))
            return

        self.updates_in.send(StatusUpdate(
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Copying...")
                                     ))

        try:
            #subprocess.check_call(["rsync", "-rI", "--delete", "--", self.source, mountpath])
            pass
        except subprocess.CalledProcessError as e:
            success = False
            print(e)
       
        # TODO: Anything less primitive?
        #time.sleep(3)
        self.updates_in.send(StatusUpdate(
                                      pendrive,
                                      DriveStatus.DRIVE_INPROGRESS,
                                      _("Unmounting...")
                                     ))

        try:
            #dbus_handler.unmount(self.path)
            pass
        except dbus.DBusException:
            self.updates_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while unmounting!")
                                         ))
            return

        if success:
            # TODO: Anything less primitive?
            #time.sleep(3)
            self.updates_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_DONE,
                                          _("Done.")
                                         ))
        else:
            self.updates_in.send(StatusUpdate(
                                          pendrive,
                                          DriveStatus.DRIVE_ERROR,
                                          _("Error while copying!")
                                         ))
