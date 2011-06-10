import gtk
import gobject
from gtk import Builder
from threading import Thread
import sys

from dispatch import EventQueue
import dispatch

class PendriveStore:
    DRIVE_NEW = 0
    DRIVE_PART_SELECTED = 1
    DRIVE_PART_WRITING = 2
    DRIVE_PART_DONE = 3
    DRIVE_ERROR = 4

    COLOR_NEW = "White"
    COLOR_DONE = "LightGreen"
    COLOR_INPROGRESS = "Gold"
    COLOR_ERROR = "Red"

    code_to_color = {
                     DRIVE_NEW: COLOR_NEW,
                     DRIVE_PART_SELECTED: COLOR_INPROGRESS,
                     DRIVE_PART_WRITING: COLOR_INPROGRESS,
                     DRIVE_PART_DONE: COLOR_INPROGRESS,
                     DRIVE_ERROR: COLOR_ERROR
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

class PendriveListWrapper:
    def __init__(self, pendrive_view):
        self.pendrive_view = pendrive_view
        self.pendrive_store = PendriveStore()
        self.pendrive_view.set_model(self.pendrive_store.store)

        self.cell_name = gtk.CellRendererText()
        self.cell_port = gtk.CellRendererText()
        self.cell_status = gtk.CellRendererText()
        self.column_name = gtk.TreeViewColumn("Nazwa", self.cell_name, text=0)
        self.column_port = gtk.TreeViewColumn("Port", self.cell_port, text=1)
        self.column_status = gtk.TreeViewColumn("Status",
                                                self.cell_status,
                                                text=PendriveStore.COLUMN_STATUSTEXT,
                                                background=PendriveStore.COLUMN_COLOR
                                               )
        self.pendrive_view.append_column(self.column_name)
        self.pendrive_view.append_column(self.column_port)
        self.pendrive_view.append_column(self.column_status)
        self.pendrive_view.get_selection().set_mode(gtk.SELECTION_NONE)

class GUI(Thread):
    __single = None

    def __init__(self):
        if GUI.__single:
            raise GUI.__single
        GUI.__single = self

        Thread.__init__(self)
        self.daemon = True

        self.builder = Builder()
        self.builder.add_from_file(sys.path[0] + "/lib/pendrive-frenzy.glade")

        self.window = self.builder.get_object("main_window")
        self.pendrive_list = PendriveListWrapper( self.builder.get_object("pendrive_list") )
        self.writing_enabled = self.builder.get_object("writing_enabled")

        self.builder.connect_signals(self)
        self.window.show()

    def run(self):
        gtk.main()
        EventQueue.instance().put(dispatch.Quit())

    @staticmethod
    def instance():
        return GUI.__single if GUI.__single else GUI()

    def on_main_window_destroy(widget, data = None):
        gtk.main_quit()

    def writing_active(self):
        return self.writing_enabled.get_active()

    def status_update(self, pendrive, status_code, status_text):
        gobject.idle_add(self.__status_update_idle, pendrive, status_code, status_text)

    def __status_update_idle(self, pendrive, status):
        print("{0}: {1} {2}".format(pendrive, status_code, status_text))

    def pendrive_add(self, pendrive, port):
        gobject.idle_add(self.__pendrive_add_idle, pendrive, port)

    def __pendrive_add_idle(self, pendrive, port):
        self.pendrive_list.pendrive_store.store.append([
            pendrive, port, "Nowy", PendriveStore.DRIVE_NEW, PendriveStore.COLOR_NEW
        ])

    def pendrive_remove(self, pendrive):
        gobject.idle_add(self.__pendrive_remove_idle, pendrive)

    def __pendrive_remove_idle(self, pendrive):
        pendrive_iter = self.pendrive_list.pendrive_store.find(pendrive)
        if pendrive_iter is None: return
        self.pendrive_list.pendrive_store.store.remove(pendrive_iter)

    def partition_add(self, part, parent):
        gobject.idle_add(self.__partition_add_idle, part, parent)

    def __partition_add_idle(self, part, parent):
        if not self.writing_active(): return
        parent_iter = self.pendrive_list.pendrive_store.find(parent)
        if parent_iter is None: return
        statuscode, statustext = self.pendrive_list.pendrive_store.get_status(parent_iter)
        if statuscode != PendriveStore.DRIVE_NEW: return
        self.pendrive_list.pendrive_store.set_status(
                                                     parent_iter,
                                                     PendriveStore.DRIVE_PART_SELECTED,
                                                     "Zapis partycji..."
                                                    )
        EventQueue.instance().put(dispatch.WriteData(part))
