from multiprocessing import Process
import signal

class DBusHandlerLauncher(Process):
    def __init__(self, events_out):
        Process.__init__(self)
        self.daemon = True
        self.events_out = events_out

    def run(self):
        from dbus_handler import DBusHandler
        import gobject
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        h = DBusHandler(self.events_out)
        loop = gobject.MainLoop()
        loop.run()
