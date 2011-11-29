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
from lib.datawriter_launcher import DataWriterSpawner

      

def main():
    (events_out, events_in) = multiprocessing.Pipe(False)
    (updates_out, updates_in) = multiprocessing.Pipe(False)
    (writers_out, writers_in) = multiprocessing.Pipe(False)

    writers = dict()

    try:
        # Spawn DBus events handler
        dbus_launcher = DBusHandlerLauncher(events_in)
        dbus_launcher.start()

        # Spawn GUI
        gui_launcher = GUILauncher(updates_out, events_in)
        gui_launcher.start()

        # Spawn Dispatch/Logic
        d = Dispatch(events_out, updates_in, writers_in)
        d.start()

        # Spawn writers on request
        dws = DataWriterSpawner(writers_out, writers, events_in)
        dws.start()

        # Join to Dispatch/Logic
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
    print(_("Terminating DataWriter sprawner..."))
    writers_in.send(None)
    dws.join()
    print(_("Terminating writers..."))
    for writer in writers:
        print("  {0}".format(writer))
        writers[writer].terminate()
        writers[writer].join()
    print(_("Terminating logic..."))
    events_in.send(Quit())
    d.join()

if __name__ == '__main__':
    main()
