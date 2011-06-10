#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import dbus
from dbus.mainloop.glib import DBusGMainLoop

gobject.threads_init()

from lib.gui import GUI
from lib.dispatch import EventQueue, Executor


def handler(*args, **kwargs):
    print("Handler activated.")
    print("Args.")
    print(args)
    print("kwArgs.")
    print(kwargs)

def main():
    DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    bus.add_signal_receiver(handler,
                            dbus_interface="org.freedesktop.UDisks",
                            path="/org/freedesktop/UDisks",
                            sender_keyword="sender",
                            destination_keyword="dest",
                            interface_keyword="iface",
                            member_keyword="member",
                            path_keyword="path"
                           )

    executor = Executor()
    gui = GUI.instance()
    gui.start()
    executor.start()
    executor.join()


if __name__ == '__main__':
    main()
