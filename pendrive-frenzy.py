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
import threading

import sys
import logging

from lib.dispatch import Dispatch
from lib.dbus_handler_launcher import DBusHandlerLauncher
from lib.gui_launcher import GUILauncher
from lib.gui_updates import Quit
from lib.datawriter_spawner import DataWriterSpawner
from lib.config_events import ReadConfig


def main():
    qevents = multiprocessing.Queue()
    qupdates = multiprocessing.Queue()
    qwriters = multiprocessing.Queue()
    qquits = multiprocessing.Queue()

    writers = dict()

    # Bus diagram
    #
    #  .______________________________________________________________.
    #  |                                                              |
    #  |                                          DBus events         |
    #  |                  updates         quits         |             |
    #  |                                               \|/       |#|  |
    #  |           main     |#|   main     |#|          '        |#|  |
    #  |          thread -->|#|  thread -->|#|--> DBusHandler -->|#|--'
    #  |          (Quit)    |#|  (Quit)    |#|                   |#| 
    #  |                    |#|                                  |#|
    #  '-> Dispatch/Logic ->|#|------------> GUI --------------->|#|
    #             |         |#|                                  |#| 
    #             |    |#|                                       |#| 
    #             '--->|#|--------------> DataWriterSpawner ---->|#| 
    #       main ----->|#|                                       |#| 
    #      thread      |#|                                    
    #      (Quit)                                              events
    #                writers
    #                         


    try:
        # Spawn DBus events handler
        dbus_launcher = DBusHandlerLauncher(qevents, qquits)
        dbus_launcher.start()

        # Spawn GUI
        gui_launcher = GUILauncher(qupdates, qevents)
        gui_launcher.start()

        # Spawn Dispatch/Logic
        d = Dispatch(qevents, qupdates, qwriters)
        d.start()

        if len(sys.argv) >= 2:
            qevents.put(ReadConfig(sys.argv[1]))
        
        # Spawn writers on request
        dws = DataWriterSpawner(qwriters, writers, qevents)
        dws.start()

        # Join to Dispatch/Logic
        d.join()
    except KeyboardInterrupt:
        qupdates.put(Quit())
    logging.info(_("Quiting... ^C will force termination."))
    logging.info(_("Terminating DBus handler..."))

    qquits.put(None)
    qquits.close()
    qquits.join_thread()
    dbus_launcher.join()

    logging.info(_("Waiting for GUI..."))
    qupdates.close()
    qupdates.join_thread()
    gui_launcher.join()

    logging.info(_("Terminating DataWriter sprawner..."))
    qwriters.put(None)
    dws.join()
    qwriters.close()
    qwriters.join_thread()

    logging.info(_("Waiting for writers..."))
    for writer in writers:
        logging.info("  {0}".format(writer))
        writers[writer].join()

    logging.info(_("Waiting for logic..."))
    qevents.close()
    qevents.join_thread()
    d.join()

    # Probably there really is a bug in multiprocessing
    # http://bugs.python.org/issue9207
    # semi-fix?
    remaining_threads = threading.enumerate()[1:]
    logging.info(_("Waiting for {0} remaining thread(s)...").format(len(remaining_threads)))
    for thread in remaining_threads:
        thread.join()

    logging.info(_("Bye."))

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(processName)s %(threadName)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    main()
