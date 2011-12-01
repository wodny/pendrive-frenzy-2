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
from datawriter_events import DataWriterRequest

class DBusEvent:
    pass

class DriveAdded(DBusEvent):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, dispatch):
        print(_("New drive: {0}").format(self.path))
        if dispatch.writing and dispatch.config:
            dispatch.drive_partitions[self.path] = set()
            dispatch.drive_partitions_awaited[self.path] = set(
                ( "{0}{1}".format(self.path, p) for p in dispatch.config.partitions )
            )
        dispatch.updates_in.put(gui_updates.DriveAdded(self.path, self.port))


class PartitionAdded(DBusEvent):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, dispatch):
        print(_("New partition: {0}").format(self.path))
        if dispatch.writing and dispatch.config:
            if self.parent in dispatch.drive_partitions:
                dispatch.drive_partitions[self.parent] |= set((self.path,))
            if dispatch.drive_partitions[self.parent] & dispatch.drive_partitions_awaited[self.parent] == dispatch.drive_partitions_awaited[self.parent]:
                for p in dispatch.drive_partitions_awaited[self.parent]:
                    dispatch.writers_in.put(DataWriterRequest(p, "le source"))

class DeviceRemoved(DBusEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        print(_("Device removed: {0}").format(self.path))
        try:
            del dispatch.drive_partitions[self.path]
        except KeyError:
            pass
        dispatch.updates_in.put(gui_updates.DeviceRemoved(self.path))
        dispatch.writers_in.put(DataWriterRequest(self.path, "le source", True))

class Dummy(DBusEvent):
    def __init__(self, text):
        self.text = text

    def handle(self, dispatch):
        print("TEXT: {0}".format(self.text))
