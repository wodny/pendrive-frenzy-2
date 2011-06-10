from datawriter import DataWriter

class Event:
    pass

class StatusUpdate(Event):
    def __init__(self, pendrive, status_code, status_text):
        self.pendrive = pendrive
        self.status_code = status_code
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
    def __init__(self, path, source_dir):
        self.path = path
        self.source_dir = source_dir

    def handle(self, executor):
        writer = DataWriter(self.path, self.source_dir)
        writer.start()

class Quit(Event):
    def __init__(self):
        pass

    def handle(self, executor):
        executor.execute = False

