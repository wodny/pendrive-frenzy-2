import dbus
from dbus.mainloop.glib import DBusGMainLoop
from dispatch import EventQueue
import events

class DBusHandler:
    __single = None


    def __init__(self):
        if DBusHandler.__single:
            raise DBusHandler.__single
        DBusHandler.__single = self

        DBusGMainLoop(set_as_default=True)
    
        self.systembus = dbus.SystemBus()
        self.systembus.add_signal_receiver(self.handler,
                                     dbus_interface="org.freedesktop.UDisks",
                                     path="/org/freedesktop/UDisks",
                                     sender_keyword="sender",
                                     destination_keyword="dest",
                                     interface_keyword="iface",
                                     member_keyword="member",
                                     path_keyword="path"
                                    )

        self.ev_queue = EventQueue.instance()

        # Assure the UDisks service runs
        self.get_device("/org/freedesktop/UDisks")

    @staticmethod
    def instance():
        return DBusHandler.__single if DBusHandler.__single else DBusHandler()

    def handler(self, *args, **kwargs):
        member = kwargs['member']
        path = args[0]
        if member == "DeviceAdded" and \
           self.is_drive(path)     and \
           self.get_conn_interface(path) == "usb":
            port = self.get_port(path)
            self.ev_queue.put(events.DriveAdded(path, port))
        if member == "DeviceAdded" and self.is_partition(path):
            self.ev_queue.put(events.PartitionAdded(path, self.get_parent(path)))
        if member == "DeviceRemoved": self.ev_queue.put(events.DeviceRemoved(path))


    def get_device(self, path):
        return self.systembus.get_object(
                                         'org.freedesktop.UDisks',
                                         path
                                        )

    def get_prop(self, device, propname):
        return device.Get(
                          'org.freedesktop.UDisks.Device',
                          propname,
                          dbus_interface = 'org.freedesktop.DBus.Properties'
                         )

    def is_drive(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DeviceIsDrive")

    def is_partition(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DeviceIsPartition")

    def get_port(self, path):
        device = self.get_device(path)
        port = self.get_prop(device, "NativePath")
        return port[port.find("/usb"): port.rfind("/host")]

    def get_parent(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "PartitionSlave")

    def mount(self, path):
        device = self.get_device(path)
        if self.get_prop(device, "DeviceIsMounted"):
            return self.get_prop(device, "DeviceMountPaths")[0]
        return device.FilesystemMount(
                                      "", [],
                                      dbus_interface = 'org.freedesktop.UDisks.Device'
                                     )

    def unmount(self, path):
        device = self.get_device(path)
        return device.FilesystemUnmount(
                                        [],
                                        dbus_interface = 'org.freedesktop.UDisks.Device'
                                       )

    def get_conn_interface(self, path):
        device = self.get_device(path)
        return self.get_prop(device, "DriveConnectionInterface")
