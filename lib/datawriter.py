# -*- coding: utf-8 -*-

import subprocess
from threading import Thread
from dispatch import EventQueue
from pendrivestore import PendriveStore
from dbus_handler import DBusHandler
import events
import time
import dbus

class DataWriter(Thread):
    def __init__(self, path, source):
        Thread.__init__(self)
        self.path = path
        self.source = source

    def run(self):
        success = True
        queue = EventQueue.instance()
        dbus_handler = DBusHandler.instance()
        pendrive = dbus_handler.get_parent(self.path)

        queue.put(events.StatusUpdate(
                                      pendrive,
                                      PendriveStore.DRIVE_INPROGRESS,
                                      _("Mounting...")
                                     ))
        try:
            mountpath = dbus_handler.mount(self.path)
        except dbus.DBusException:
            queue.put(events.StatusUpdate(
                                          pendrive,
                                          PendriveStore.DRIVE_ERROR,
                                          _("Error while mounting!")
                                         ))
            return

        queue.put(events.StatusUpdate(
                                      pendrive,
                                      PendriveStore.DRIVE_INPROGRESS,
                                      _("Copying...")
                                     ))

        try:
            subprocess.check_call(["rsync", "-rI", "--delete", "--", self.source, mountpath])
        except subprocess.CalledProcessError as e:
            success = False
            print(e)
       
        # TODO: Anything less primitive?
        time.sleep(1)
        queue.put(events.StatusUpdate(
                                      pendrive,
                                      PendriveStore.DRIVE_INPROGRESS,
                                      _("Unmounting...")
                                     ))

        try:
            dbus_handler.unmount(self.path)
        except dbus.DBusException:
            queue.put(events.StatusUpdate(
                                          pendrive,
                                          PendriveStore.DRIVE_ERROR,
                                          _("Error while unmounting!")
                                         ))
            return

        if success:
            # TODO: Anything less primitive?
            time.sleep(2)
            queue.put(events.StatusUpdate(
                                          pendrive,
                                          PendriveStore.DRIVE_DONE,
                                          _("Done.")
                                         ))
        else:
            queue.put(events.StatusUpdate(
                                          pendrive,
                                          PendriveStore.DRIVE_ERROR,
                                          _("Error while copying!")
                                         ))
