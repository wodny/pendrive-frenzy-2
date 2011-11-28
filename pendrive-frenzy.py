#!/usr/bin/python

import gettext
gettext.install("pendrive-frenzy", "locale")

# Bind for PyGTK
import locale
locale.bindtextdomain("pendrive-frenzy", "locale")

#import pygtk
#pygtk.require('2.0')
#import gtk
#import gobject
#
#gobject.threads_init()
#
#from lib.gui import GUI
#from lib.dispatch import EventQueue, Executor
#from lib.dbus_handler import DBusHandler

import signal
import multiprocessing
from lib.dispatch import Dispatch
from lib.master_events import Quit
from lib.dbus_handler_launcher import DBusHandlerLauncher

def main():
    (events_out, events_in) = multiprocessing.Pipe(False)
    try:
        dbus_launcher = DBusHandlerLauncher(events_in)
        dbus_launcher.start()

        d = Dispatch(events_out)
        d.start()
        d.join()
    except KeyboardInterrupt:
        print(_("Quiting... another ^C will force termination."))
        events_in.send(Quit())
        d.join()
        print(_("Terminating DBus handler..."))
        dbus_launcher.terminate()
        dbus_launcher.join()
    #executor = Executor()
    #dbus_handler = DBusHandler.instance()
    #gui = GUI.instance()
    #gui.start()
    #executor.gui = gui
    #executor.dbus = dbus_handler
    #executor.start()
    #executor.join()


if __name__ == '__main__':
    main()
