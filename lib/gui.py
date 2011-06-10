import gtk
import gobject
from gtk import Builder
from threading import Thread
import sys

from dispatch import EventQueue
import dispatch

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
        #self.progressbar = self.builder.get_object("progressbar_file")
        #self.total_progressbar = self.builder.get_object("progressbar_total")
        #self.errors = self.builder.get_object("errors_text")
        #self.errors_expander = self.builder.get_object("errors_expander")
        #self.main_status = self.builder.get_object("main_status")

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

    def progress_update(self, progress, total_progress, status):
        gobject.idle_add(self.__progress_update_idle, progress, total_progress, status)

    def __progress_update_idle(self, progress, total_progress, status):
        self.progressbar.set_fraction(progress / 100.0)
        self.total_progressbar.set_fraction(total_progress / 100.0)
        if status is not None:
            self.progressbar.set_text(status)

    def status_update(self, status):
        gobject.idle_add(self.__status_update_idle, status)

    def __status_update_idle(self, status):
        self.total_progressbar.set_text(status)

    def mainstatus_update(self, status):
        gobject.idle_add(self.__mainstatus_update_idle, status)

    def __mainstatus_update_idle(self, status):
        self.main_status.set_text(status)

    def errors_update(self, errors):
        gobject.idle_add(self.__errors_update_idle, errors)
    
    def __errors_update_idle(self, errors):
        buffer = self.errors.get_buffer()
        buffer.insert(buffer.get_end_iter(), errors)

    def expand_errors(self, really = True):
        gobject.idle_add(self.__expand_errors_idle, really)
    
    def __expand_errors_idle(self, really):
        self.errors_expander.set_expanded(really)
