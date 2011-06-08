import gtk
import gobject

from trayicon import TrayIcon

class GUI:
    __single = None

    def __init__(self):
        if GUI.__single:
            raise GUI.__single

        GUI.__single = self
        self.trayicon = TrayIcon()

    @staticmethod
    def instance():
        return GUI.__single if GUI.__single else GUI()

    def quit(self):
        gobject.idle_add(self.__quit_idle)

    def __quit_idle(self):
        gtk.main_quit()
