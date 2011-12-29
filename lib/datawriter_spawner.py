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
import logging

class DataWriterSpawner(Thread):
    def __init__(self, writers_out, writers, events_in):
        Thread.__init__(self)
        self.writers_out = writers_out
        self.writers = writers
        self.events_in = events_in
        self.name = "SpawnerThread"

    def run(self):
        logging.debug(_("DataWriterSpawner running..."))
        writer_req = self.writers_out.get()
        while writer_req:
            writer_req.handle(self.writers, self.events_in)
            writer_req = self.writers_out.get()
        logging.info(_("DataWriterSpawner exiting..."))
        self.writers_out.close()
        self.writers_out.join_thread()
