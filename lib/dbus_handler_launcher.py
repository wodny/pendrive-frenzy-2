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



from multiprocessing import Process
import signal

class DBusHandlerLauncher(Process):
    def __init__(self, events_out):
        Process.__init__(self)
        self.daemon = True
        self.events_out = events_out

    def run(self):
        from dbus_handler import DBusHandler
        import gobject
        gobject.threads_init()
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        h = DBusHandler(self.events_out)
        loop = gobject.MainLoop()
        loop.run()
        #import time
        #import dbus_events
        #i = 0
        #while i < 10:
        #    self.events_out.put(dbus_events.Dummy("DBusHandlerLauncher"))
        #    i += 1
        #    time.sleep(3)
