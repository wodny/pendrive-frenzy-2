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

import logging

class DataWriterRemoval:
    def __init__(self, device):
        self.device = device

    def handle(self, writers, events_in):
        logging.debug(_("DataWriter removal request ({0})").format(self.device))
        if self.device not in writers:
            logging.error(_("DataWriter for {0} not found!").format(self.device))
            return
        del writers[self.device]
        logging.debug(_("Removed DataWriter for {0}.").format(self.device))
