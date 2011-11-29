#!/usr/bin/python

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

    # Bus diagram
    #
    #  .______________________________________________________.
    #  |                                                      |
    #  |                                  DBus events         |
    #  |                    updates             |             |
    #  |                                       \|/       |#|  |
    #  |                      |#|               '        |#|  |
    #  |                      |#|         DBusHandler -->|#|--'
    #  |                      |#|                        |#| 
    #  '-> Dispatch/Logic --->|#|--> GUI --------------->|#|
    #             |           |#|                        |#| 
    #             |      |#|                             |#| 
    #             '----->|#|------> DataWriterSpawner -->|#| 
    #                    |#|                             |#| 
    #                    |#|                                
    #                                                  events
    #                  writers
    #                         


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
    print(_("Bye."))

if __name__ == '__main__':
    main()
