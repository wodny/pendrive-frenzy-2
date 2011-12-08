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



import gui_updates
from drive_statuses import DriveStatus


class DataWriterRequest:
    def __init__(self, destination, source, remove = False):
        self.destination = destination
        self.source = source
        self.remove = remove

class DataWriterEvent:
    pass

class StatusUpdate(DataWriterEvent):
    def __init__(self, parent, partition, status_code, status_text):
        self.parent = parent
        self.partition = partition
        self.status_code = status_code
        self.status_text = status_text

    def handle(self, dispatch):
        # TODO: Probably we should catch sth if someone removes a drive in progress
        dispatch.drive_partitions[self.parent][self.partition] = self.status_code
        dispatch.update_gui_status(self.parent)
        dispatch.updates_in.put(
            gui_updates.StatusBarUpdate(self.status_text)
        )
        
class DataWriterDone(DataWriterEvent):
    def __init__(self, destination, source, remove):
        self.destination = destination
        self.source = source
        self.remove = remove

    def handle(self, dispatch):
        dispatch.writers_in.put(DataWriterRequest(self.destination, self.source, True))
