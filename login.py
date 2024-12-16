import sys
import threading
import webbrowser

import gi
import requests
import json

from PyThreadKiller import PyThreadKiller

from api_reference import TokenHandler
from login_server import LoginServer
from main_screen import MainWindow
from reset_password import ResetPasswordWindow
from sign_up import SignUpWindow

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gdk, Adw
import os
import signal

class Login(Gtk.ApplicationWindow):
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
            self.accountingCssProvider.load_from_path("src/css/MainScreen.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            main_box = Gtk.Box()
            main_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_box, "MainWindow")
            self.stack.set_visible_child_name("MainWindow")
            # AccountingPage(main_box)
            MainWindow(main_box,self.stack)
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
            self.accountingCssProvider.load_from_path("src/css/MainScreen.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            main_box = Gtk.Box()
            main_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_box, "MainWindow")
            self.stack.set_visible_child_name("MainWindow")
            # AccountingPage(main_box)
            MainWindow(main_box,self.stack)

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

    def on_forgot_password_clicked(self, button):
        # self.close()
        ResetPasswordWindow()
        # subprocess.run(["python3", "reset_password.py"])

    def show_dialog(self, info):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=info
        )
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.show()

    def on_sign_in_clicked(self, button):
        account = self.account_entry.get_text()
        password = self.password_entry.get_text()
        print(f"Account: {account}, Password: {password}")
        self.login(account, password)

    def on_sign_up_clicked(self, button):
        # self.close()
        SignUpWindow()
        # subprocess.run(["python3", "sign_up.py"])

    def login(self, username: str, password) -> json:
        with open(
                "config.json",
                "r",
        ) as f:
            CONFIG = json.load(f)
        login_url = f"{CONFIG['base_url']}auth/login/"
        response = self.session.post(
            login_url, json={"username": username, "password": password}
        )
        if response.status_code == 200:
            print("登入成功:", response.json())
            TokenHandler().generate_and_save_key()
            TokenHandler().save_token_encrypted(response.json()["token"])

            Gtk.StyleContext().remove_provider_for_display(Gdk.Display.get_default(), self.thirdLoginCssProvider)

            self.accountingCssProvider = Gtk.CssProvider()
            self.accountingCssProvider.load_from_path("src/css/MainScreen.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            main_box = Gtk.Box()
            main_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_box, "MainWindow")
            self.stack.set_visible_child_name("MainWindow")
            # AccountingPage(main_box)
            MainWindow(main_box,self.stack)

            return response.json()
        else:
            print("登入失敗:", response.json())
            error_message = response.json().get("error", "無法處理請求")
            self.show_dialog(f"Error：{error_message}")
            return response.json()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stack = Gtk.Stack()
        self.session = requests.Session()
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
        # Main Box
        self.accountingCssProvider = None
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.set_name("MainBox")
        self.stack.add_named(main_box, "ThirdLogin")
        self.set_child(self.stack)
        # Label: Third Party Sign In
        sign_in_label = Gtk.Label(label="Sign in")
        sign_in_label.set_name("ThirdPartySign")
        sign_in_label.set_margin_bottom(20)
        main_box.append(sign_in_label)

        self.account_entry = Gtk.Entry()
        self.account_entry.set_placeholder_text("Account")
        self.account_entry.set_margin_bottom(10)
        self.account_entry.set_width_chars(20)
        main_box.append(self.account_entry)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Password")
        self.password_entry.set_margin_bottom(10)
        self.password_entry.set_width_chars(20)
        self.password_entry.set_visibility(False)
        main_box.append(self.password_entry)

        sign_in_button = Gtk.Button(label="Sign in")
        sign_in_button.set_name("sign_in_button")
        sign_in_button.set_halign(Gtk.Align.FILL)
        sign_in_button.connect("clicked", self.on_sign_in_clicked)
        main_box.append(sign_in_button)

        sign_up_button = Gtk.Button(label="Sign up")
        sign_up_button.set_name("sign_in_button")
        sign_up_button.set_halign(Gtk.Align.FILL)
        sign_up_button.connect("clicked", self.on_sign_up_clicked)
        main_box.append(sign_up_button)

        forgot_password_button = Gtk.Button(label="Forgot password?")
        forgot_password_button.set_name("forgot_password_button")
        forgot_password_button.set_halign(Gtk.Align.CENTER)
        forgot_password_button.add_css_class("link")
        forgot_password_button.connect("clicked", self.on_forgot_password_clicked)
        main_box.append(forgot_password_button)

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
        self.thirdLoginCssProvider.load_from_path("src/css/MainScreen.css")
        Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.thirdLoginCssProvider,
                                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        github_sign_in_button.connect("clicked", self.githubLogin)
        google_sign_in_button.connect("clicked", self.googleLogin)

        self.login_server = LoginServer()
        if response.status_code == 200:
            # Login Success
            self.accountingCssProvider = Gtk.CssProvider()
            self.accountingCssProvider.load_from_path("src/css/MainScreen.css")
            Gtk.StyleContext().add_provider_for_display(Gdk.Display.get_default(), self.accountingCssProvider,
                                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            main_screen_box = Gtk.Box()
            main_screen_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.stack.add_named(main_screen_box, "MainWindow")
            self.stack.set_visible_child_name("MainWindow")
            # AccountingPage(main_box,date="2024")
            MainWindow(main_screen_box,self.stack)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.connect("window-removed", self.on_destroy)

    def on_activate(self, app):
        self.win = Login(application=app)
        self.win.set_name("Login")
        self.win.set_size_request(700, 500)
        self.win.present()
        self.win.set_name("body")
        self.win.connect("close-request", self.on_destroy)

    def on_destroy(self, data):
        os.kill(os.getpid(), signal.SIGTERM)
        pass


app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
