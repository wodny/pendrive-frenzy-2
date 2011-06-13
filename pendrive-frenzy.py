#!/usr/bin/python

import gettext
gettext.install("pendrive-frenzy", "locale")

# Bind for PyGTK
import locale
locale.bindtextdomain("pendrive-frenzy", "locale")

import pygtk
pygtk.require('2.0')
import gtk
import gobject

gobject.threads_init()

from lib.gui import GUI
from lib.dispatch import EventQueue, Executor
from lib.dbus_handler import DBusHandler


def main():
    executor = Executor()
    dbus_handler = DBusHandler.instance()
    gui = GUI.instance()
    gui.start()
    executor.gui = gui
    executor.dbus = dbus_handler
    executor.start()
    executor.join()


if __name__ == '__main__':
    main()
