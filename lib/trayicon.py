import gtk

class Popup(gtk.Menu):
    def __init__(self):
        gtk.Menu.__init__(self)


class TrayIcon(gtk.StatusIcon):
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.set_from_stock(gtk.STOCK_PASTE)
