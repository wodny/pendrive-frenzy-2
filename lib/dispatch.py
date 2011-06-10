import Queue
from threading import Thread, Timer


class EventQueue(Queue.Queue):
    __single = None

    def __init__(self):
        if EventQueue.__single:
            raise EventQueue.__single

        Queue.Queue.__init__(self)
        EventQueue.__single = self

    @staticmethod
    def instance():
        return EventQueue.__single if EventQueue.__single else EventQueue()


class Executor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.queue = EventQueue.instance()
        self.execute = True
        self.gui = None
        self.dbus = None

    def run(self):
        while self.execute:
            order = self.queue.get()
            order.handle(self)
