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

class DataWriterSpawner(Thread):
    def __init__(self, writers_out, writers, events_in):
        Thread.__init__(self)
        self.writers_out = writers_out
        self.writers = writers
        self.events_in = events_in

    #def new_datawriter(self, writer_req):
    #    dw = DataWriterLauncher(self.events_in, writer_req)
    #    self.writers[writer_req.destination] = dw
    #    dw.start()

    #def del_datawriter(self, writer_req):
    #    del self.writers[writer_req.destination]

    def run(self):
        writer_req = self.writers_out.get()
        while writer_req:
            writer_req.handle(self.writers, self.events_in)

            #if writer_req.remove:
            #    if writer_req.destination in self.writers:
            #        self.del_datawriter(writer_req)
            #        print("Removed writer for {0}".format(writer_req.destination))
            #else:
            #    if writer_req.destination in self.writers:
            #        print("Already writing this destination")
            #    else:
            #        print("New writer for {0}".format(writer_req.destination))
            #        self.new_datawriter(writer_req)
            writer_req = self.writers_out.get()
        print("DataWriter spawner exiting...")
        self.writers_out.close()
        self.writers_out.join_thread()
