#    Copyright 2011  Marcin Szewczyk <Marcin.Szewczyk@wodny.org>
#
#    This file is part of pendrive-frenzy.
#
#    Pendrive-frenzy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pendrive-frenzy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pendrive-frenzy.  If not, see <http://www.gnu.org/licenses/>.



import gtk
from drive_statuses import DriveStatus

class PendriveStore:
    COLOR_NEW = "White"
    COLOR_DONE = "LightGreen"
    COLOR_INPROGRESS = "Gold"
    COLOR_ERROR = "Red"

    code_to_color = {
                     DriveStatus.DRIVE_NEW: COLOR_NEW,
                     DriveStatus.DRIVE_HASPT: COLOR_INPROGRESS,
                     DriveStatus.DRIVE_INPROGRESS: COLOR_INPROGRESS,
                     DriveStatus.DRIVE_WAITFORPT: COLOR_INPROGRESS,
                     DriveStatus.DRIVE_PTERROR: COLOR_INPROGRESS,
                     DriveStatus.DRIVE_DONE: COLOR_DONE,
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
        try:
            color = PendriveStore.code_to_color[code]
        except KeyError:
            color = PendriveStore.COLOR_ERROR if code & DriveStatus.DRIVE_ERROR else PendriveStore.COLOR_NEW

        self.store.set(
                       iter,
                       PendriveStore.COLUMN_STATUSCODE, code,
                       PendriveStore.COLUMN_STATUSTEXT, text,
                       PendriveStore.COLUMN_COLOR, color
                      )

