import re

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import subprocess
import requests
import json
import datetime

session = requests.Session()

class SignUpWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 500)
        self.present()
        # self.set_css()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        self.set_name("body")
        self.set_child(main_box)

        sign_up_label = Gtk.Label(label="Sign up")
        sign_up_label.set_name("ThirdPartySign")
        sign_up_label.set_margin_bottom(20)
        main_box.append(sign_up_label)


        self.account_entry = Gtk.Entry()
        self.account_entry.set_placeholder_text("Account")
        self.account_entry.set_name("account_entry")
        self.account_entry.set_margin_bottom(10)
        self.account_entry.set_width_chars(20)
        main_box.append(self.account_entry)

        self.email_entry = Gtk.Entry()
        self.email_entry.set_placeholder_text("Email")
        self.email_entry.set_name("email_entry")
        self.email_entry.set_margin_bottom(10)
        self.email_entry.set_width_chars(20)
        main_box.append(self.email_entry)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Password")
        self.password_entry.set_name("password_entry")
        self.password_entry.set_margin_bottom(10)
        self.password_entry.set_width_chars(20)
        self.password_entry.set_visibility(False)
        main_box.append(self.password_entry)

        self.confirm_password_entry = Gtk.Entry()
        self.confirm_password_entry.set_placeholder_text("Confirm password")
        self.confirm_password_entry.set_name("confirm_password_entry")
        self.confirm_password_entry.set_margin_bottom(10)
        self.confirm_password_entry.set_width_chars(20)
        self.confirm_password_entry.set_visibility(False)
        main_box.append(self.confirm_password_entry)

        sign_up_button = Gtk.Button(label="Sign up")
        sign_up_button.set_name("sign_in_button")
        sign_up_button.set_halign(Gtk.Align.FILL)
        sign_up_button.connect("clicked", self.on_sign_up_clicked)
        main_box.append(sign_up_button)

    def on_sign_up_clicked(self, button):
        account = self.account_entry.get_text()
        email = self.email_entry.get_text()
        password = self.password_entry.get_text()
        confirm_password = self.confirm_password_entry.get_text()
        if password != confirm_password:
            self.show_dialog("Passwords do not match. Please try again.")
        
        else:
            print(f"Account: {account}, Email: {email}, Password: {password}, Confirm password: {confirm_password}")
            self.register(account, password, email)

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

    def show_successed_dialog(self):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text = "Registration Successful"
        )

        def on_successed_response(dialog, response):
            dialog.destroy()
            self.close()
            subprocess.run(["python3", "sign_in.py"])

        dialog.connect("response", on_successed_response)
        dialog.show()

    def register(self, username: str, password: str, email: str) -> json:
        with open(
                "config.json",
                "r",
        ) as f:
            CONFIG = json.load(f)
        register_url = f"{CONFIG['base_url']}auth/register/"
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            self.show_dialog("Please enter a valid email address.")
            return
        new_user_data = {
            "username": username,
            "password": password,
            "email": email,
        }
        response = session.post(register_url, json=new_user_data)
        if response.status_code == 201:
            self.show_successed_dialog()
            return response.json()
        else:
            self.show_dialog(f"Registration Failed\n\n{response.json()["error"]}")
            return response.json()


# if __name__ == "__main__":
#     app = Gtk.Application()
#
#     def on_activate(app):
#         win = LoginWindow()
#         win.set_application(app)
#         win.present()
#
#     app.connect("activate", on_activate)
#     app.run()
