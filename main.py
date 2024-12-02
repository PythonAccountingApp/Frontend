import sys
import threading
import webbrowser

import gi
import requests
import json

from gi.repository.Gtk import CssProvider

import api_reference

from PyThreadKiller import PyThreadKiller

from AccountingPage import AccountingPage
from api_reference import TokenHandler
from login_server import LoginServer

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gdk, Adw
import os
import signal


class MainWindow(Gtk.ApplicationWindow):
    def githubLoginThread(self):
        if not self.login_server.server_status:
            self.login_server.LoginServerStart()
        with open(
                "config.json",
                "r",
        ) as f:
            CONFIG = json.load(f)
        webbrowser.open(f'https://github.com/login/oauth/authorize?client_id={CONFIG['github']['client_id']}', new=2)
        while self.login_server.callbackData is None or self.login_server.callbackData == "ERROR":
            pass

        print(self.login_server.callbackData)

        url = f"https://github.com/login/oauth/access_token?client_id={CONFIG['github']['client_id']}&client_secret={CONFIG['github']['secret_key']}&code={self.login_server.callbackData}"
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.request("GET", url, headers=headers)

        responseText = response.text.split("&")
        accessCode = responseText[0].split("=")[1]
        tokenType = responseText[2].split("=")[1]
        session = requests.Session()
        response = session.post(f"{CONFIG['base_url']}auth/github/",
                                json={"access_token": accessCode, "token_type": tokenType})

        print(response.json())
        if response.status_code == 200:
            TokenHandler().generate_and_save_key()
            TokenHandler().save_token_encrypted(response.json()["token"])

            Gtk.StyleContext().remove_provider_for_display(Gdk.Display.get_default(), self.thirdLoginCssProvider)

            self.accountingCssProvider = Gtk.CssProvider()
            self.accountingCssProvider.load_from_path("src/css/AccountingAdd.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.stack.remove(self.stack.get_child_by_name("ThirdLogin"))
            main_box = Gtk.Box()
            main_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_box, "AccountingAdd")
            AccountingPage(main_box)

            self.login_server.callbackData = None
            self.login_server.server_status = False
            self.login_server.serverThread.kill()

        else:
            if self.login_server.callbackData is not None or self.login_server.callbackData != "ERROR":
                pass
            else:
                print(f"ERROR:{response.json()}")
        return False

    def githubLogin(self, button):
        thread = threading.Thread(target=self.githubLoginThread)
        if not self.login_server.server_status:
            self.login_server.serverThread = PyThreadKiller(self.login_server.run_server)
        thread.start()

    def googleLoginThread(self):
        if not self.login_server.server_status:
            self.login_server.LoginServerStart()
        with open(
                "config.json",
                "r",
        ) as f:
            CONFIG = json.load(f)
        webbrowser.open(
            f'https://accounts.google.com/o/oauth2/v2/auth/auth?client_id={CONFIG['google']['client_id']}&redirect_uri=http://localhost:53269/google/callback&response_type=token&scope=https://www.googleapis.com/auth/userinfo.email',
            new=2)
        while self.login_server.callbackData is None or self.login_server.callbackData == "ERROR":
            pass
        session = requests.Session()
        response = session.post(f"{CONFIG['base_url']}auth/google/",
                                json={"access_token": self.login_server.callbackData[0],
                                      "token_type": self.login_server.callbackData[0]})

        if response.status_code == 200:
            TokenHandler().generate_and_save_key()
            TokenHandler().save_token_encrypted(response.json()["token"])

            Gtk.StyleContext().remove_provider_for_display(Gdk.Display.get_default(), self.thirdLoginCssProvider)

            self.accountingCssProvider = Gtk.CssProvider()
            self.accountingCssProvider.load_from_path("src/css/AccountingAdd.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.stack.remove(self.stack.get_child_by_name("ThirdLogin"))
            main_box = Gtk.Box()
            main_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_box, "AccountingAdd")
            AccountingPage(main_box)

            self.login_server.callbackData = None
            self.login_server.server_status = False
            self.login_server.serverThread.kill()


        else:
            if self.login_server.callbackData is not None or self.login_server.callbackData != "ERROR":
                pass
            else:
                print(f"ERROR:{response.status_code}")
        return False

    def googleLogin(self, button):
        thread = threading.Thread(target=self.googleLoginThread)
        if not self.login_server.server_status:
            self.login_server.serverThread = PyThreadKiller(self.login_server.run_server)
        thread.start()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stack = Gtk.Stack()
        with open(
                "config.json",
                "r",
        ) as f:
            CONFIG = json.load(f)
        token = TokenHandler().load_token_encrypted()
        categories_url = f"{CONFIG['base_url']}categories/"
        header = {"Authorization": f"Token {token}"}
        session = requests.Session()
        response = session.get(
            categories_url, headers=header
        )
        if response.status_code == 200:
            # Login Success
            self.accountingCssProvider = Gtk.CssProvider()
            self.accountingCssProvider.load_from_path("src/css/AccountingAdd.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            main_box = Gtk.Box()
            main_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_box, "AccountingAdd")
            self.set_child(self.stack)
            AccountingPage(main_box)
        else:
            # Login Fail
            # Main Box
            self.accountingCssProvider = None
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            main_box.set_hexpand(True)
            main_box.set_vexpand(True)
            main_box.set_halign(Gtk.Align.CENTER)
            main_box.set_valign(Gtk.Align.CENTER)
            main_box.set_name("MainBox")

            # Label: Third Party Sign In
            third_party_sign = Gtk.Label(label="Third Party Sign In")
            third_party_sign.set_name("ThirdPartySign")
            main_box.append(third_party_sign)

            # Github Sign In Button
            github_sign_in_button = Gtk.Button()
            github_sign_in_button.set_name("GithubSignIn")
            github_sign_in_button.set_size_request(215, 65)
            github_sign_in_button.set_halign(Gtk.Align.CENTER)
            github_sign_in_button.set_valign(Gtk.Align.FILL)
            main_box.append(github_sign_in_button)

            # Github Sign In Button
            google_sign_in_button = Gtk.Button()
            google_sign_in_button.set_name("GoogleSignIn")
            google_sign_in_button.set_size_request(215, 65)
            google_sign_in_button.set_halign(Gtk.Align.CENTER)
            google_sign_in_button.set_valign(Gtk.Align.FILL)
            main_box.append(google_sign_in_button)

            self.thirdLoginCssProvider = Gtk.CssProvider()
            self.thirdLoginCssProvider.load_from_path("src/css/ThirdLogin.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.thirdLoginCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

            github_sign_in_button.connect("clicked", self.githubLogin)
            google_sign_in_button.connect("clicked", self.googleLogin)


            self.stack.add_named(main_box, "ThirdLogin")
            self.set_child(self.stack)
            self.login_server = LoginServer()


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.connect("window-removed", self.on_destroy)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.set_name("MainWindow")
        self.win.set_size_request(600, 500)
        self.win.present()
        self.win.connect("close-request", self.on_destroy)

    def on_destroy(self, data):
        os.kill(os.getpid(), signal.SIGTERM)
        pass


app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
