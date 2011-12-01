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


import signal
import multiprocessing
from multiprocessing import Process
from threading import Thread

from lib.dbus_handler_launcher import DBusHandlerLauncher

class Dispatch(Process):
    def __init__(self, events_out, updates_in, writers_in):
        Process.__init__(self)
        self.work = True
        self.events_out = events_out
        self.updates_in = updates_in
        self.writers_in = writers_in
        self.writing = None
        self.config = None

        self.drive_partitions = dict()
        self.drive_partitions_awaited = dict()
        self.drive_partitions_done = dict()
        self.drive_partitions_failed = dict()

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while self.work:
            order = self.events_out.get()
            order.handle(self)

        self.updates_in.close()
        self.updates_in.join_thread()
        self.writers_in.close()
        self.writers_in.join_thread()
        self.events_out.close()
        self.events_out.join_thread()
