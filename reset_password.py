import re

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import subprocess
import requests
import json
import datetime

session = requests.Session()


class ResetPasswordWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Reset Password")
        self.set_default_size(600, 400)
        self.present()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        self.set_child(main_box)
        self.set_name("body")

        reset_password_label = Gtk.Label(label="Reset Password")
        reset_password_label.set_name("ThirdPartySign")
        reset_password_label.set_margin_bottom(20)
        main_box.append(reset_password_label)

        self.email_entry = Gtk.Entry()
        self.email_entry.set_placeholder_text("Email")
        self.email_entry.set_name("email_entry")
        self.email_entry.set_margin_bottom(10)
        self.email_entry.set_width_chars(20)
        main_box.append(self.email_entry)

        submit_button = Gtk.Button(label="Submit")
        submit_button.set_name("sign_in_button")
        submit_button.set_halign(Gtk.Align.FILL)
        submit_button.connect("clicked", self.on_submit_clicked)
        main_box.append(submit_button)

    def on_submit_clicked(self, button):
        email = self.email_entry.get_text()
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            self.show_dialog("Please enter a valid email address.")
            return
        with open(
                "config.json",
                "r",
        ) as f:
            CONFIG = json.load(f)
        reset_password_url = f"{CONFIG['base_url']}/auth/password-reset/"
        if not email:
            self.show_dialog("Please enter a valid email address.")
            return

        try:
            response = session.post(reset_password_url, json={"email": email})
            if response.status_code == 200:
                self.show_successed_dialog()
            else:
                error_message = response.json().get("error", "無法處理請求")
                self.show_dialog(f"Error：{error_message}")
        except Exception as e:
            self.show_dialog(f"Request Failed：{str(e)}")

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
            text="The password reset email has been sent. Please check your inbox."
        )

        def on_successed_response(dialog, response):
            dialog.destroy()
            self.close()

        dialog.connect("response", on_successed_response)
        dialog.show()
