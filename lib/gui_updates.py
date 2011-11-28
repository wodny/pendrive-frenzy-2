class GUIUpdate:
    pass

class DriveAdded(GUIUpdate):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, updater):
        updater.gui.pendrive_add(self.path, self.port)
