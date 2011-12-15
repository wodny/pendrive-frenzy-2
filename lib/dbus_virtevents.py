# Because currently UDisks' DeviceJobChanged is not very useful, this 
# wrapper is used.

from drive_statuses import DriveStatus
from partition_statuses import PartitionStatus
import tools
from datawriter_requests import PartitionCreatorRequest, PartitionWriterRequest

class DBusVirtEvent:
    pass

class MBRCreated(DBusVirtEvent):
    def __init__(self, drive):
        self.drive = drive

    def handle(self, dispatch):
        print(_("Partition table created: {0}").format(self.drive))
        dispatch.drive_statuses[self.drive] = DriveStatus.DRIVE_HASPT
        dispatch.update_status(self.drive, "New MBR for {0}.".format(self.drive))

        awaited = \
            dispatch.get_partitions_by_status(self.drive, PartitionStatus.AWAITED)
        for p in awaited:
            dispatch.drive_partitions[self.drive][p] = PartitionStatus.IN_PROGRESS
            partspec = dispatch.config.partspecs[tools.partnumber(self.drive, p)]
            dispatch.writers_in.put(PartitionCreatorRequest(self.drive, p, partspec))

class FSCreated(DBusVirtEvent):
    def __init__(self, drive, part):
        self.drive = drive
        self.part = part

    def handle(self, dispatch):
        print("Filesystem created on {0}.".format(self.part))

        dispatch.account_partition_added(None, self.drive, self.part)
        dispatch.drive_partitions[self.drive][self.part] = PartitionStatus.IN_PROGRESS
        dispatch.update_status(self.drive, "New partition {0}.".format(self.part))

        partspec = dispatch.config.partspecs[tools.partnumber(self.drive, self.part)]
        dispatch.writers_in.put(PartitionWriterRequest(self.drive, self.part, partspec))
