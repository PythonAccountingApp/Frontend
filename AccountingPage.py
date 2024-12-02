import json

import gi

import re

from gi.repository.Gdk import Cursor
from pycparser.ply.yacc import token

from api_reference import TokenHandler, CategoryHandler, ExpenseHandler

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class AccountingPage(Gtk.ApplicationWindow):
    def __init__(self, main_box):
        super().__init__()
        print("ss")
        self.main_box = Gtk.Box()
        self.main_box = main_box
        self.main_box.set_size_request(width=1000, height=600)
        self.input_boxs = dict()
        self.selected = ['', 0]
        self.rend_ui(main=self.main_box)

    def rend_ui(self, main):
        main.set_homogeneous(True)
        left_box = Gtk.Box()
        left_box.set_homogeneous(True)
        left_box.set_orientation(Gtk.Orientation.VERTICAL)
        left_box.set_hexpand(True)
        left_box.set_vexpand(True)

        expense_scrolled = Gtk.ScrolledWindow()
        self.expense_box = Gtk.Box()
        self.expense_box.set_orientation(Gtk.Orientation.VERTICAL)
        expense_scrolled.set_hexpand(True)
        expense_scrolled.set_vexpand(True)
        expense_scrolled.set_margin_top(15)
        expense_scrolled.set_margin_start(15)
        expense_scrolled.set_name("Block")
        expense_scrolled.set_has_frame(False)
        expense_scrolled.set_child(self.expense_box)

        income_scrolled = Gtk.ScrolledWindow()
        self.income_box = Gtk.Box()
        self.income_box.set_orientation(Gtk.Orientation.VERTICAL)
        income_scrolled.set_hexpand(True)
        income_scrolled.set_vexpand(True)
        income_scrolled.set_margin_top(15)
        income_scrolled.set_margin_bottom(15)
        income_scrolled.set_margin_start(15)
        income_scrolled.set_name("Block")
        income_scrolled.set_child(self.income_box)
        left_box.append(expense_scrolled)
        left_box.append(income_scrolled)

        GLib.idle_add(self.create_category_button)

        main.append(left_box)

        right_box = Gtk.Box()
        right_box.new(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        right_box.set_spacing(20)
        right_box.set_orientation(Gtk.Orientation.VERTICAL)
        right_box.set_hexpand(True)
        right_box.set_vexpand(True)
        right_box.set_name("Block")
        right_box.set_margin_top(15)
        right_box.set_margin_bottom(15)
        right_box.set_margin_start(15)
        right_box.set_margin_end(15)

        self.input_boxs["description"] = Gtk.Entry()
        self.input_boxs["description"].set_placeholder_text("Description")
        right_box.append(self.input_boxs["description"])

        self.input_boxs["store"] = Gtk.Entry()
        self.input_boxs["store"].set_placeholder_text("Store")
        right_box.append(self.input_boxs["store"])

        self.input_boxs["amount"] = Gtk.Entry()
        self.input_boxs["amount"].set_editable(True)
        self.input_boxs["amount"].set_placeholder_text("Amount")
        self.input_boxs["amount"].connect("changed", self.amount_entry_changed)
        right_box.append(self.input_boxs["amount"])

        self.input_boxs["discount"] = Gtk.Entry()
        self.input_boxs["discount"].set_editable(True)
        self.input_boxs["discount"].set_placeholder_text("Discount")
        self.input_boxs["discount"].connect("changed", self.amount_entry_changed)
        right_box.append(self.input_boxs["discount"])

        # Time Select
        if True:
            time_select_box = Gtk.Box()
            time_select_box.set_orientation(Gtk.Orientation.HORIZONTAL)
            time_select_box.set_spacing(10)

            time_label = Gtk.Label()
            time_label.set_label("Time:")
            time_label.set_halign(Gtk.Align.START)
            time_label.set_name("TimeLabel")
            time_select_box.append(time_label)

            space_box = Gtk.Box()
            space_box.set_hexpand(True)
            time_select_box.append(space_box)

            self.input_boxs["hour_spin_button"] = Gtk.SpinButton()
            self.input_boxs["hour_spin_button"].set_orientation(Gtk.Orientation.VERTICAL)
            hour_adjustment = Gtk.Adjustment()
            hour_adjustment.set_lower(0)
            hour_adjustment.set_upper(23)
            hour_adjustment.set_step_increment(1)
            self.input_boxs["hour_spin_button"].connect("changed", self.spin_changed)
            self.input_boxs["hour_spin_button"].set_adjustment(hour_adjustment)
            time_select_box.append(self.input_boxs["hour_spin_button"])

            between_h_m = Gtk.Label()
            between_h_m.set_label(":")
            time_select_box.append(between_h_m)

            self.input_boxs["minute_spin_button"] = Gtk.SpinButton()
            self.input_boxs["minute_spin_button"].set_orientation(Gtk.Orientation.VERTICAL)
            minute_adjustment = Gtk.Adjustment()
            minute_adjustment.set_lower(0)
            minute_adjustment.set_upper(59)
            minute_adjustment.set_step_increment(1)
            self.input_boxs["minute_spin_button"].connect("changed", self.spin_changed)
            self.input_boxs["minute_spin_button"].set_adjustment(minute_adjustment)
            time_select_box.append(self.input_boxs["minute_spin_button"])

            between_m_s = Gtk.Label()
            between_m_s.set_label(":")
            time_select_box.append(between_m_s)

            self.input_boxs["second_spin_button"] = Gtk.SpinButton()
            self.input_boxs["second_spin_button"].set_orientation(Gtk.Orientation.VERTICAL)
            second_adjustment = Gtk.Adjustment()
            second_adjustment.set_lower(0)
            second_adjustment.set_upper(59)
            second_adjustment.set_step_increment(1)
            self.input_boxs["second_spin_button"].connect("changed", self.spin_changed)
            self.input_boxs["second_spin_button"].set_adjustment(second_adjustment)
            time_select_box.append(self.input_boxs["second_spin_button"])

        if True:
            detail_box = Gtk.Box()
            detail_box.set_orientation(Gtk.Orientation.HORIZONTAL)
            detail_box.set_spacing(15)

            detail_label = Gtk.Label()
            detail_label.set_label("Detail:")
            detail_label.set_halign(Gtk.Align.START)
            detail_label.set_name("TimeLabel")
            detail_box.append(detail_label)

            detail_scroll_window = Gtk.ScrolledWindow()
            detail_scroll_window.set_hexpand(True)
            detail_scroll_window.set_size_request(-1, 100)
            self.input_boxs["detail"] = Gtk.TextView()
            self.input_boxs["detail"].set_name("InputBox")
            self.input_boxs["detail"].set_editable(True)
            detail_scroll_window.set_child(self.input_boxs["detail"])
            detail_box.append(detail_scroll_window)
            right_box.append(detail_box)
            right_box.append(time_select_box)

        v_space_box = Gtk.Box()
        v_space_box.set_vexpand(True)
        right_box.append(v_space_box)

        save_button = Gtk.Button()
        save_button.set_valign(Gtk.Align.END)
        save_button.set_halign(Gtk.Align.END)
        save_button.set_label("Save")
        save_button.set_name("SaveButton")
        save_button.connect("clicked", self.save_button_onclick)
        right_box.append(save_button)

        main.append(right_box)

    def create_category_button(self):
        left_box_width = self.expense_box.get_width()
        if left_box_width == 0:
            return True
        now_line_width = 0
        self.expense_button_list = list()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.token = TokenHandler().load_token_encrypted()
        print(self.token)
        categories = CategoryHandler.get_all_categories(self.token)
        expense = [i for i in categories if i['category_type'] == 'expense']
        income = [i for i in categories if i['category_type'] == 'income']

        expense_label = Gtk.Label()
        expense_label.set_text("Expense")
        expense_label.set_halign(Gtk.Align.START)
        expense_label.set_name("TypeLabel")
        self.expense_box.append(expense_label)

        for category in expense:
            button = Gtk.Button()
            button.set_label(category['name'])
            button.set_name("CategoryButton")
            button.set_valign(Gtk.Align.START)
            button.set_halign(Gtk.Align.START)

            button_width = button.get_preferred_size()[1].width + 10
            self.expense_button_list.append(button)

            button.connect("clicked", self.category_button_clicked, 0, category['id'])
            if now_line_width + button_width < left_box_width:
                hbox.append(button)
                now_line_width += button_width
            else:
                self.expense_box.append(hbox)
                now_line_width = button_width  # 新一行的寬度設為當前按鈕的寬度
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                hbox.append(button)

        self.expense_box.append(hbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        now_line_width = 0

        income_label = Gtk.Label()
        income_label.set_text("Income")
        income_label.set_halign(Gtk.Align.START)
        income_label.set_name("TypeLabel")
        self.income_box.append(income_label)

        for category in income:
            button = Gtk.Button()
            button.set_label(category['name'])
            button.set_name("CategoryButton")
            button.set_valign(Gtk.Align.START)
            button.set_halign(Gtk.Align.START)

            button_width = button.get_preferred_size()[1].width + 10
            self.expense_button_list.append(button)

            button.connect("clicked", self.category_button_clicked, 1, category['id'])
            if now_line_width + button_width < left_box_width:
                hbox.append(button)
                now_line_width += button_width
            else:
                self.income_box.append(hbox)
                now_line_width = button_width  # 新一行的寬度設為當前按鈕的寬度
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                hbox.append(button)

        self.income_box.append(hbox)

        return False  # 停止重複執行

    def category_button_clicked(self, button, type, category):
        self.selected = ["expense" if type == 0 else "income", category]
        print(self.selected)
        for expense_button in self.expense_button_list:
            expense_button.set_name("CategoryButton")
        button.set_name("Selected")
        pass

    def amount_entry_changed(self, entry):
        GLib.idle_add(self.amount_entry_check, entry)

    def amount_entry_check(self, entry):
        text = "" + entry.get_text()
        regex_result_num = re.search("^\\d*$", entry.get_text())
        regex_result_float = re.search("^-?\\d+(\\.)?(\\d+)?$", entry.get_text())
        if not ((regex_result_num or regex_result_float) and len(text) != 0):
            entry.set_text("" if len(text) - 1 < 0 else text[:(len(text) - 1)])
            entry.set_position(-1)

    def spin_changed(self, entry):
        GLib.idle_add(self.spin_check, entry)

    def spin_check(self, entry):
        text = "" + entry.get_text()
        regex_result_num = re.search("^\\d*$", entry.get_text())
        if not (regex_result_num and len(text) != 0):
            entry.set_text("0" if len(text) - 1 < 0 else text[:(len(text) - 1)])
            entry.set_position(-1)

    def save_button_onclick(self, button):
        texts = {}
        if self.selected[0] == '':
            button.set_label("Please select one category.")
            return
        for key, value in self.input_boxs.items():
            if key != "detail":
                text = value.get_text()
            else:
                buffer = value.get_buffer()
                startIter, endIter = buffer.get_bounds()
                text = buffer.get_text(startIter, endIter, False)
            if text.isspace() or len(text) == 0:
                button.set_label("All fields need to be filled in with values.")
                return
            texts[key] = text
            print(text)
        response = ExpenseHandler().create_expense(token=self.token,transaction_type=self.selected[0], category=self.selected[1],
                                        description=texts["description"], store=texts["store"],
                                        amount=float(texts["amount"]), discount=float(texts["discount"]),
                                        time=f"{texts["hour_spin_button"].zfill(2)}:{texts["minute_spin_button"].zfill(2)}:{texts["second_spin_button"].zfill(2)}",
                                        detail=texts["detail"])
        if response.status_code == 201:
            print("SUCCESS")
        else:
            button.set_label("Error.Please re-login.")



"""token: str,
   transaction_type: str,
   category: int,
   description: str,
   store: str,
   amount: float = 0,
   discount: float = 0,
   date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
   time: str = datetime.datetime.now().strftime("%H:%M:%S"),
   detail: str = """""
