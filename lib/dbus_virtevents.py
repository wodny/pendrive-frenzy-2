# Because currently UDisks' DeviceJobChanged is not very useful, this 
# wrapper is used.

from drive_statuses import DriveStatus

class DBusVirtEvent:
    pass

class PartitionsCreated(DBusVirtEvent):
    def __init__(self, drive):
        self.drive = drive

    def handle(self, dispatch):
        print(_("Partition table created: {0}").format(self.drive))
        dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_PTDONE
        dispatch.update_gui_status(self.drive)

        # TODO
        # FS creation here and worker right after that
        # Set part. statuses as available/in progress
