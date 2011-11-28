import gui_updates

class DBusEvent:
    pass

class DriveAdded(DBusEvent):
    def __init__(self, path, port):
        self.path = path
        self.port = port

    def handle(self, dispatch):
        print(_("New drive: {0}").format(self.path))
        dispatch.updates_in.send(gui_updates.DriveAdded(self.path, self.port))

class PartitionAdded(DBusEvent):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    def handle(self, dispatch):
        print(_("New partition: {0}").format(self.path))
        dispatch.updates_in.send(gui_updates.PartitionAdded(self.path, self.port))

class DeviceRemoved(DBusEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        print(_("Device removed: {0}").format(self.path))
        dispatch.updates_in.send(gui_updates.DeviceRemoved(self.path))
