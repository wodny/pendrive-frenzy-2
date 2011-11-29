class GUIUpdate:
    pass

class DriveAdded(GUIUpdate):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, updater):
        updater.gui.pendrive_add(self.path, self.port)

# TODO: UNTESTED
class PartitionAdded(GUIUpdate):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, updater):
        updater.gui.partition_add(self.path, self.port)

class DeviceRemoved(GUIUpdate):
    def __init__(self, path):
        self.path = path

    def handle(self, updater):
        updater.gui.pendrive_remove(self.path)

class StatusUpdate(GUIUpdate):
    def __init__(self, pendrive, status_code, status_text):
        self.pendrive = pendrive
        self.status_code = status_code
        self.status_text = status_text

    def handle(self, updater):
        updater.gui.status_update(self.pendrive, self.status_code, self.status_text)
