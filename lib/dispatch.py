import signal
import multiprocessing
from multiprocessing import Process
from threading import Thread

from lib.dbus_handler_launcher import DBusHandlerLauncher

class Dispatch(Process):
    def __init__(self, events_out, updates_in):
        Process.__init__(self)
        #self.daemon = True
        self.work = True
        self.events_out = events_out
        self.updates_in = updates_in

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while self.work:
            order = self.events_out.recv()
            order.handle(self)
