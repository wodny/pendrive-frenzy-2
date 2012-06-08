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


from datawriter_launcher import MBRWriterLauncher, FullDriveWriterLauncher, PartitionWriterLauncher
import logging


class DataWriterRequest:
    pass


class PartitionWriterRequest(DataWriterRequest):
    def __init__(self, parent, part, partspec):
        self.parent = parent
        self.part = part
        self.partspec = partspec

    def handle(self, writers, events_in):
        logging.debug(
            _("Requested PartitionDataWriter for {0}.").format(
                self.part
            )
        )
        if self.part in writers:
            logging.error(
                _("Already have PartitionDataWriter for {0}!").format(
                    self.part
                )
            )
            return
        logging.debug(
            _("Spawning PartitionDataWriter for {0}...").format(
                self.part
            )
        )
        l = PartitionWriterLauncher(events_in, self)
        writers[self.part] = l
        l.start()


class MBRWriterRequest(DataWriterRequest):
    def __init__(self, drive, config):
        self.drive = drive
        self.config = config
        self.partspecs = config.partspecs

    def handle(self, writers, events_in):
        logging.debug(_("Requested MBRWriter for {0}.").format(self.drive))
        if self.drive in writers:
            logging.error(
                _("Already have MBRWriter for {0}!").format(
                    self.drive
                )
            )
            return
        logging.debug(_("Spawning MBRWriter for {0}...").format(self.drive))
        l = MBRWriterLauncher(events_in, self)
        writers[self.drive] = l
        l.start()

class FullDriveWriterRequest(DataWriterRequest):
    def __init__(self, drive, config):
        self.drive = drive
        self.config = config
        self.partspecs = config.partspecs

    def handle(self, writers, events_in):
        logging.debug(_("Requested FullDriveWriter for {0}.").format(self.drive))
        if self.drive in writers:
            logging.error(
                _("Already have FullDriveWriter for {0}!").format(
                    self.drive
                )
            )
            return
        logging.debug(_("Spawning FullDriveWater for {0}...").format(self.drive))
        l = FullDriveWriterLauncher(events_in, self)
        writers[self.drive] = l
        l.start()
