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

import logging
import optparse

from lib.dispatch import Dispatch
from lib.dbus_handler_launcher import DBusHandlerLauncher
from lib.gui_launcher import GUILauncher
from lib.gui_updates import Quit
from lib.datawriter_spawner import DataWriterSpawner
from lib.config_events import ReadConfig


def main(configfilename):
    # Drive status updates, GUI events
    qevents = multiprocessing.Queue()
    # GUI update instructions
    qupdates = multiprocessing.Queue()
    # DataWriter requests
    qwriters = multiprocessing.Queue()
    # A queue to quit the DBusHandler
    qquits = multiprocessing.Queue()
    # Flag signalled when any module wants to quit
    quiting = multiprocessing.Event()

    writers = dict()

    # Bus diagram
    #
    #  .______________________________________________________________.
    #  |                                                              |
    #  |                                          DBus events         |
    #  |                  updates         quits         |             |
    #  |                                               \|/       |#|  |
    #  |           main     |#|   main     |#|          '        |#|  |
    #  |      .-- thread -->|#|  thread -->|#|--> DBusHandler -->|#|--'
    #  |      |   (Quit)    |#|  (Quit)    |#|                   |#|
    #  |     \|/            |#|                                  |#|
    #  |      '             |#|                                  |#|
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
        d = Dispatch(quiting, qevents, qupdates, qwriters)
        d.start()

        qevents.put(ReadConfig(configfilename))

        # Spawn writers on request
        dws = DataWriterSpawner(qwriters, writers, qevents)
        dws.start()

        # Wait until a module signals the application should quit
        quiting.wait()
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

    logging.info(_("Terminating DataWriter spawner..."))
    qwriters.put(None)
    dws.join()
    qwriters.close()
    qwriters.join_thread()

    logging.info(_("Waiting for writers..."))
    for writer in writers:
        logging.info("  {0}".format(writer))
        writers[writer].join()

    logging.info(_("Waiting for logic..."))
    qevents.put(None)
    d.join()
    qevents.close()
    qevents.join_thread()
    d.join()

    # Probably there really is a bug in multiprocessing
    # http://bugs.python.org/issue9207
    # semi-fix?
    remaining_threads = threading.enumerate()[1:]
    logging.info(
        _("Waiting for {0} remaining thread(s)...").format(
            len(remaining_threads)
        )
    )
    for thread in remaining_threads:
        thread.join()

    logging.info(_("Bye."))


def init_logging(options):
    logformat = "%(asctime)s %(levelname)s" \
                "%(processName)s %(threadName)s" \
                "%(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    numeric_level = getattr(logging, options.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {0}".format(options.loglevel))

    logging.basicConfig(
        level=numeric_level,
        format=logformat,
        datefmt=datefmt
    )

    if options.enablelogfile:
        fhandler = logging.FileHandler(options.logfile)
        fhandler.setFormatter(logging.Formatter(logformat, datefmt))

        rootlogger = logging.getLogger()
        rootlogger.addHandler(fhandler)


def parse_options():
    usage = _("usage: %prog [options] <configfile>")
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "-l", "--loglevel",
        default="INFO",
        help=_("log level")
    )
    parser.add_option(
        "-w", "--enablelogfile",
        action="store_true",
        dest="enablelogfile",
        default=False,
        help=_("should logging to a file be enabled")
    )
    parser.add_option(
        "-f", "--logfile",
        default="pendrive-frenzy.log",
        help=_("log filename")
    )
    return parser.parse_args()

if __name__ == '__main__':
    (options, args) = parse_options()
    if len(args) < 1:
        exit(_("Config filename required."))
    init_logging(options)
    main(args[0])
