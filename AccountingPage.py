from gi.repository import Gtk

class AccountingPage(Gtk.ApplicationWindow):
    def __init__(self,mainWindow):
        super().__init__()
        print("sss")

    def window(self):
        print("Window")