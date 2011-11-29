import gtk
from drive_statuses import DriveStatus

class PendriveStore:
    COLOR_NEW = "White"
    COLOR_DONE = "LightGreen"
    COLOR_INPROGRESS = "Gold"
    COLOR_ERROR = "Red"

    code_to_color = {
                     DriveStatus.DRIVE_NEW: COLOR_NEW,
                     DriveStatus.DRIVE_SELECTED: COLOR_INPROGRESS,
                     DriveStatus.DRIVE_INPROGRESS: COLOR_INPROGRESS,
                     DriveStatus.DRIVE_DONE: COLOR_DONE,
                     DriveStatus.DRIVE_ERROR: COLOR_ERROR
                    }

    COLUMN_STATUSTEXT = 2
    COLUMN_STATUSCODE = 3
    COLUMN_COLOR = 4


    def __init__(self):
        self.store = gtk.ListStore(str, str, str, int, str)

    def find(self, path):
        iter = self.store.get_iter_first()
        while iter:
            if self.store.get(iter, 0)[0] == path: return iter
            iter = self.store.iter_next(iter)

    def get_status(self, iter):
        return self.store.get(iter, PendriveStore.COLUMN_STATUSCODE, PendriveStore.COLUMN_STATUSTEXT)

    def set_status(self, iter, code, text):
        color = PendriveStore.code_to_color[code]
        self.store.set(
                       iter,
                       PendriveStore.COLUMN_STATUSCODE, code,
                       PendriveStore.COLUMN_STATUSTEXT, text,
                       PendriveStore.COLUMN_COLOR, color
                      )

