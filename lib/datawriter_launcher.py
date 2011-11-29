from threading import Thread
from multiprocessing import Process
import signal


class DataWriterSpawner(Thread):
    def __init__(self, writers_out, writers, events_in):
        Thread.__init__(self)
        self.writers_out = writers_out
        self.writers = writers
        self.events_in = events_in

    def run(self):
        writer_req = self.writers_out.recv()
        while writer_req:
            if writer_req.destination not in self.writers:
                print("New writer")
                dw = DataWriterLauncher(self.events_in, writer_req.destination, writer_req.source)
                self.writers[writer_req.destination] = dw
                dw.start()
            else:
                if writer_req.remove:
                    del self.writers[writer_req.destination]
                    print("Removed writer for {0}".format(writer_req.destination))
                else:
                    print("Already writing this destination")
            writer_req = self.writers_out.recv()
        print("DataWriter spawner exiting...")



class DataWriterLauncher(Process):
    def __init__(self, events_in, destination, source):
        Process.__init__(self)
        self.daemon = True
        self.events_in = events_in
        self.destination = destination
        self.source = source

    def run(self):
        from datawriter import DataWriter
        print("Running")
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        w = DataWriter(self.events_in, self.destination, self.source)
        w.run()
