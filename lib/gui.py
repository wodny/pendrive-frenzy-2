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



import pygtk
pygtk.require('2.0')
import gtk
import gobject

gobject.threads_init()

from gtk import Builder
from threading import Thread
import sys

from gui_events import *

from pendrivestore import PendriveStore
from drive_statuses import DriveStatus

class PendriveListWrapper:
    def __init__(self, pendrive_view):
        self.pendrive_view = pendrive_view
        self.pendrive_store = PendriveStore()
        self.pendrive_view.set_model(self.pendrive_store.store)

        self.cell_name = gtk.CellRendererText()
        self.cell_port = gtk.CellRendererText()
        self.cell_status = gtk.CellRendererText()
        self.column_name = gtk.TreeViewColumn(_("Device"), self.cell_name, text=0)
        self.column_port = gtk.TreeViewColumn(_("Port"), self.cell_port, text=1)
        self.column_status = gtk.TreeViewColumn(_("Status"),
                                                self.cell_status,
                                                text=PendriveStore.COLUMN_STATUSTEXT,
                                                background=PendriveStore.COLUMN_COLOR
                                               )
        self.pendrive_view.append_column(self.column_name)
        self.pendrive_view.append_column(self.column_port)
        self.pendrive_view.append_column(self.column_status)
        self.pendrive_view.get_selection().set_mode(gtk.SELECTION_NONE)


class Updater(Thread):
    def __init__(self, updates_out, gui):
        Thread.__init__(self)
        self.daemon = True

        self.updates_out = updates_out
        self.gui = gui

    def run(self):
        while True:
            update = self.updates_out.get()
            update.handle(self)


class GUI:
    def __init__(self, updates_out, events_in):
        self.updates_out = updates_out
        self.events_in = events_in

        self.builder = Builder()
        self.builder.add_from_file(sys.path[0] + "/lib/pendrive-frenzy.glade")

        self.window = self.builder.get_object("main_window")
        self.pendrive_list = PendriveListWrapper( self.builder.get_object("pendrive_list") )
        self.writing_enabled = self.builder.get_object("writing_enabled")
        self.source_dir = self.builder.get_object("source_dir")

        self.builder.connect_signals(self)
        self.window.show()

    def loop(self):
        updater = Updater(self.updates_out, self)
        updater.start()

        gtk.main()
        self.events_in.put(Quit())

    @staticmethod
    def instance():
        return GUI.__single if GUI.__single else GUI()

    def on_main_window_destroy(self, widget, data = None):
        gtk.main_quit()

    def on_select_source_dir_pressed(self, widget, data = None):
        chooser = gtk.FileChooserDialog(
                                        action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_OPEN, gtk.RESPONSE_OK)
                                       )
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            source = chooser.get_filename()
            if not source.endswith('/'): source += '/'
            self.source_dir.set_text(source)
        chooser.destroy()

    def on_writing_pressed(self, widget, data = None):
        active = self.writing_active()
        self.source_dir.set_sensitive(active)
        self.events_in.put(WritingChanged(not active, self.source_dir.get_text()))

    def writing_active(self):
        return self.writing_enabled.get_active()

    def status_update(self, pendrive, status_code, status_text):
        gobject.idle_add(self.__status_update_idle, pendrive, status_code, status_text)

    def __status_update_idle(self, pendrive, status_code, status_text):
        pendrive = self.pendrive_list.pendrive_store.find(pendrive)
        if pendrive is None: return
        self.pendrive_list.pendrive_store.set_status(
                                                     pendrive,
                                                     status_code,
                                                     status_text
                                                    )

    def pendrive_add(self, pendrive, port):
        gobject.idle_add(self.__pendrive_add_idle, pendrive, port)

    def __pendrive_add_idle(self, pendrive, port):
        self.pendrive_list.pendrive_store.store.append([
            pendrive, port, _("New"), DriveStatus.DRIVE_NEW, PendriveStore.COLOR_NEW
        ])

    def pendrive_remove(self, pendrive):
        gobject.idle_add(self.__pendrive_remove_idle, pendrive)

    def __pendrive_remove_idle(self, pendrive):
        pendrive_iter = self.pendrive_list.pendrive_store.find(pendrive)
        if pendrive_iter is None: return
        self.pendrive_list.pendrive_store.store.remove(pendrive_iter)

    #def partition_add(self, part, parent):
    #    gobject.idle_add(self.__partition_add_idle, part, parent)

    #def __partition_add_idle(self, part, parent):
    #    #if not self.writing_active(): return
    #    #parent_iter = self.pendrive_list.pendrive_store.find(parent)
    #    #if parent_iter is None: return
    #    #statuscode, statustext = self.pendrive_list.pendrive_store.get_status(parent_iter)
    #    #if statuscode != PendriveStore.DRIVE_NEW: return
    #    #self.pendrive_list.pendrive_store.set_status(
    #    #                                             parent_iter,
    #    #                                             PendriveStore.DRIVE_SELECTED,
    #    #                                             _("Writing data...")
    #    #                                            )
    #    #source_dir = self.source_dir.get_text()
    #    ##EventQueue.instance().put(events.WriteData(part, source_dir))
    #    pass
