import sys
import webbrowser

import gi
import threading

from login_server import GithubLoginServer

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository.Gtk import Widget, BoxClass
from gi.repository import Gtk, Gdk, Adw

class MainWindow(Gtk.ApplicationWindow):

    def githubLoginThread(self):
        tis = GithubLoginServer()
        tis.GithubLoginServerStart()
        webbrowser.open('https://github.com/login/oauth/authorize?client_id=Ov23lioWPPeA5G5sBzFk', new=2)
        while tis.callbackData is None:
            pass
        self.githubToken.set_text(tis.callbackData)
        # print(tis.callbackData)

    def githubLogin(self,button):
        thread =threading.Thread(target = self.githubLoginThread)
        thread.start()
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here
        builder = Gtk.Builder()
        builder.add_from_file("frontend/ui.ui")
        mainBox = builder.get_object("MainScreen")

        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path("frontend/ui.css")
        Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), cssProvider,
                                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        githubLoginButton = builder.get_object("GithubSignInButton")
        githubLoginButton.connect("clicked",self.githubLogin)
        self.githubToken = builder.get_object("GithubToken")

        self.set_child(mainBox)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_size_request(600, 500)
        self.win.present()


app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
