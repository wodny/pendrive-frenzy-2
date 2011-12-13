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

from datawriter_launcher import MBRWriterLauncher, PartitionWriterLauncher

class DataWriterRequest:
    pass

class PartitionWriterRequest(DataWriterRequest):
    def __init__(self, parent, part, partspec):
        self.parent = parent
        self.part = part
        self.partspec = partspec

    def handle(self, writers, events_in):
        print("PARTITION WRITER REQUEST {0} {1} {2}".format(self.parent, self.part, self.partspec))
        if self.part in writers:
            print("Already have writer for this part.")
            return
        print("Spawning writer")
        l = PartitionWriterLauncher(events_in, self)
        writers[self.part] = l
        l.start()

class MBRWriterRequest(DataWriterRequest):
    def __init__(self, drive, partspecs):
        self.drive = drive
        self.partspecs = partspecs

    def handle(self, writers, events_in):
        print("MBR WRITER REQUEST {0}".format(self.drive))
        if self.drive in writers:
            print("Already have writer for this device.")
            return
        print("Spawning MBR writer")
        l = MBRWriterLauncher(events_in, self)
        writers[self.drive] = l
        l.start()

