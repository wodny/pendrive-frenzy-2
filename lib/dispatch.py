import signal
import multiprocessing
from multiprocessing import Process
from threading import Thread

from lib.dbus_handler_launcher import DBusHandlerLauncher

class Dispatch(Process):
    def __init__(self, queue):
        Process.__init__(self)
        #self.daemon = True
        self.work = True
        self.queue = queue

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while self.work:
            #order = self.queue.get()
            order = self.queue.recv()
            order.handle(self)
