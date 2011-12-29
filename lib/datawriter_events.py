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
from datawriter_removal import DataWriterRemoval
import logging

class DataWriterEvent:
    pass

class StatusUpdate(DataWriterEvent):
    def __init__(self, parent, parent_status, part, part_status, status_text):
        self.parent = parent
        self.parent_status = parent_status
        self.part = part
        self.part_status = part_status
        self.status_text = status_text

    def handle(self, dispatch):
        # TODO: Probably we should catch sth if someone removes a drive in progress
        if self.parent and self.parent_status is not None:
            dispatch.drive_statuses[self.parent] = self.parent_status
        if self.part and self.part_status is not None:
            dispatch.drive_partitions[self.parent][self.part] = self.part_status
            logging.debug(_("Partitions status: {0}").format(dispatch.drive_partitions[self.parent]))
        dispatch.update_status(self.parent, self.status_text)
        
class DataWriterDone(DataWriterEvent):
    def __init__(self, device):
        self.device = device

    def handle(self, dispatch):
        logging.debug(_("DataWriter for {0} done.").format(self.device))
        dispatch.writers_in.put(DataWriterRemoval(self.device))
