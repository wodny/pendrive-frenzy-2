import Queue
from threading import Thread, Timer

##########
# Events #
##########

class Event:
    pass

class StatusUpdate(Event):
    def __init__(self, pendrive, status_code, status_text):
        self.pendrive = pendrive
        self.status_code = self.status_code
        self.status_text = status_text

    def handle(self, executor):
        executor.gui.status_update(self.pendrive, self.status_code, self.status_text)

class DriveAdded(Event):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, executor):
        print("New drive: {0}".format(self.path))
        executor.gui.pendrive_add(self.path, self.port)

class PartitionAdded(Event):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, executor):
        print("New partition: {0}".format(self.path))
        executor.gui.partition_add(self.path, self.parent)

class DriveRemoved(Event):
    def __init__(self, path):
        self.path = path

    def handle(self, executor):
        print("Drive removed: {0}".format(self.path))
        executor.gui.pendrive_remove(self.path)


class WriteData(Event):
    def __init__(self, path):
        self.path = path

    def handle(self, executor):
        import time
        executor.dbus.mount(self.path)
        time.sleep(5)
        executor.dbus.unmount(self.path)

class Quit(Event):
    def __init__(self):
        pass

    def handle(self, executor):
        executor.execute = False


####################
# Queue & Executor #
####################

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
