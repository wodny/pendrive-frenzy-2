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


from threading import Thread
from multiprocessing import Process
import signal

class DBusHandlerQuiter(Thread):
    def __init__(self, loop, quits_out):
        Thread.__init__(self)
        self.loop = loop
        self.quits_out = quits_out

    def run(self):
        self.quits_out.get()
        import gobject
        gobject.idle_add(self.loop.quit)
        self.quits_out.close()
        self.quits_out.join_thread()



class DBusHandlerLauncher(Process):
    def __init__(self, events_in, quits_out):
        Process.__init__(self)
        self.events_in = events_in
        self.quits_out = quits_out
    
    def run(self):
        from dbus_handler import DBusHandler
        import gobject
        gobject.threads_init()
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        h = DBusHandler(self.events_in)
        loop = gobject.MainLoop()

        q = DBusHandlerQuiter(loop, self.quits_out)
        q.start()

        loop.run()

        self.events_in.close()
        self.events_in.join_thread()
        self.quits_out.close()
        self.quits_out.join_thread()
