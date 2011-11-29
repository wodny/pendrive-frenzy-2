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
from datawriter import DataWriter

class WriterRequest:
    def __init__(self, destination, source, remove = False):
        self.destination = destination
        self.source = source
        self.remove = remove

class DBusEvent:
    pass

class DriveAdded(DBusEvent):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, dispatch):
        print(_("New drive: {0}").format(self.path))
        dispatch.updates_in.send(gui_updates.DriveAdded(self.path, self.port))
        if dispatch.writing:
            dispatch.writers_in.send(WriterRequest(self.path, "le source"))

class PartitionAdded(DBusEvent):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, dispatch):
        print(_("New partition: {0}").format(self.path))
        #dispatch.updates_in.send(gui_updates.PartitionAdded(self.path, self.parent))

class DeviceRemoved(DBusEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        print(_("Device removed: {0}").format(self.path))
        dispatch.updates_in.send(gui_updates.DeviceRemoved(self.path))
        dispatch.writers_in.send(WriterRequest(self.path, "le source", True))
