#!/usr/bin/python

import gettext
gettext.install("pendrive-frenzy", "locale")

# Bind for PyGTK
import locale
locale.bindtextdomain("pendrive-frenzy", "locale")

import multiprocessing
from lib.dispatch import Dispatch
from lib.master_events import Quit
from lib.dbus_handler_launcher import DBusHandlerLauncher
from lib.gui_launcher import GUILauncher

def main():
    (events_out, events_in) = multiprocessing.Pipe(False)
    (updates_out, updates_in) = multiprocessing.Pipe(False)
    try:
        dbus_launcher = DBusHandlerLauncher(events_in)
        dbus_launcher.start()

        gui_launcher = GUILauncher(updates_out, events_in)
        gui_launcher.start()

        d = Dispatch(events_out, updates_in)
        d.start()
        d.join()
    except KeyboardInterrupt:
        pass
    print(_("Quiting... ^C will force termination."))
    print(_("Terminating DBus handler..."))
    dbus_launcher.terminate()
    dbus_launcher.join()
    print(_("Terminating GUI..."))
    gui_launcher.terminate()
    gui_launcher.join()
    print(_("Terminating logic..."))
    events_in.send(Quit())
    d.join()

if __name__ == '__main__':
    main()
