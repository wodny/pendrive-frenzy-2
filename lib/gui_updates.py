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



class GUIUpdate:
    pass

class DriveAdded(GUIUpdate):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, updater):
        updater.gui.pendrive_add(self.path, self.port)

# TODO: UNTESTED
class PartitionAdded(GUIUpdate):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, updater):
        updater.gui.partition_add(self.path, self.port)

class DeviceRemoved(GUIUpdate):
    def __init__(self, path):
        self.path = path

    def handle(self, updater):
        updater.gui.pendrive_remove(self.path)

class StatusUpdate(GUIUpdate):
    def __init__(self, pendrive, status_code, status_text):
        self.pendrive = pendrive
        self.status_code = status_code
        self.status_text = status_text

    def handle(self, updater):
        updater.gui.status_update(self.pendrive, self.status_code, self.status_text)
