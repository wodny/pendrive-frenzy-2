from multiprocessing import Process
import signal


class GUILauncher(Process):
    def __init__(self, updates_out, events_in):
        Process.__init__(self)
        self.events_in = events_in
        self.updates_out = updates_out

    def run(self):
        from gui import GUI
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        g = GUI(self.updates_out, self.events_in)
        g.loop()
