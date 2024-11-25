import sys
import threading
import webbrowser

import gi
import requests
import json

from flask.cli import load_dotenv
# from dotenv import load_dotenv
from login_server import GithubLoginServer

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gdk, Adw
import os
import signal


class MainWindow(Gtk.ApplicationWindow):

    def githubLoginThread(self):
        tis = GithubLoginServer()
        tis.GithubLoginServerStart()
        webbrowser.open('https://github.com/login/oauth/authorize?client_id=Ov23liw65tS7UK7PUOx7', new=2)
        while tis.callbackData is None:
            pass
        self.githubToken.set_text(tis.callbackData)

        load_dotenv()
        print(tis.callbackData)
        with open(
            "config.json",
            "r",
        ) as f:
            CONFIG = json.load(f)
        url = f"https://github.com/login/oauth/access_token?client_id=Ov23liw65tS7UK7PUOx7&client_secret={CONFIG['github']['secret_key']}&code={tis.callbackData}"
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.request("GET", url, headers=headers)

        responseText = response.text.split("&")
        accessCode=responseText[0].split("=")[1]
        tokenType=responseText[2].split("=")[1]
        print(f"accessCode={accessCode}")
        session = requests.Session()
        new_user_data = {
            "username": "123",
            "password": "123",
            "email": "",
        }
        response = session.post("http://0.0.0.0:8000/auth/register/", json=new_user_data)
        print(response.json())
        response = session.post("http://0.0.0.0:8000/auth/github/", json={"access_token":accessCode,"token_type":tokenType})
        print(response.json())
    def githubLogin(self, button):
        thread = threading.Thread(target=self.githubLoginThread)
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
        githubLoginButton.connect("clicked", self.githubLogin)
        self.githubToken = builder.get_object("GithubToken")

        self.set_child(mainBox)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.connect("window-removed",self.on_destroy)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_name("MainWindow")
        self.win.set_size_request(600, 500)
        self.win.present()
        self.win.connect("close-request",self.on_destroy)


    def on_destroy(self,data):
        os.kill(os.getpid(), signal.SIGTERM)
        pass


app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
