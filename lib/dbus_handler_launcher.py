from multiprocessing import Process
import signal

class DBusHandlerLauncher(Process):
    #def __init__(self, recv, send):
    def __init__(self, queue):
        Process.__init__(self)
        self.daemon = True
        self.queue = queue
        #self.recv = recv
        #self.send = send

    def run(self):
        from dbus_handler import DBusHandler
        import gobject
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        #h = DBusHandler(self.recv, self.send)
        h = DBusHandler(self.queue)
        loop = gobject.MainLoop()
        loop.run()
