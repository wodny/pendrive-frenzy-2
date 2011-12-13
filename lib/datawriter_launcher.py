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
from datawriter_events import DataWriterDone

class DataWriterLauncher(Process):
    def __init__(self, events_in, request):
        Process.__init__(self)
        self.events_in = events_in
        self.request = request

    def prerun(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def postrun(self):
        self.events_in.close()
        self.events_in.join_thread()


class MBRWriterLauncher(DataWriterLauncher):
    def __init__(self, events_in, request):
        DataWriterLauncher.__init__(self, events_in, request)

    def run(self):
        self.prerun()
        from datawriter import MBRWriter
        w = MBRWriter(self.events_in, self.request)
        w.run()
        self.events_in.put(DataWriterDone(self.request.drive))
        self.postrun()


class PartitionWriterLauncher(DataWriterLauncher):
    def __init__(self, events_in, request):
        DataWriterLauncher.__init__(self, events_in, request)

    def run(self):
        self.prerun()
        from datawriter import PartitionWriter
        w = PartitionWriter(self.events_in, self.request)
        w.run()
        self.events_in.put(DataWriterDone(self.request.part))
        self.postrun()
