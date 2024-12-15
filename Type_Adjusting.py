import sys
import gi
import calendar
import datetime
import os
import json
import requests
import time

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw
from cryptography.fernet import Fernet
from api_reference import TokenHandler,ExpenseHandler,CategoryHandler
from typing import cast


# css_provider = Gtk.CssProvider()
# css_provider.load_from_path('style.css')
# Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

class TypeAdjusting(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(":D")
        self.bottom_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,homogeneous=False,vexpand=True,hexpand=True,name="background",height_request=600,width_request=450)
        self.set_child(self.bottom_box)
        self.up_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,homogeneous=True,hexpand=True,name="up_box",css_classes=['container'])
        self.bottom_box.append(self.up_box)

        self.down_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,homogeneous=True,vexpand=True,hexpand=True,name="up_box",css_classes=['container'])
        self.bottom_box.append(self.down_box)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)  # 切換動畫
        self.stack.set_transition_duration(500)  # 動畫時間（毫秒）

        # 添加頁面到 Stack
        self.expense_scrolledwindow=Gtk.ScrolledWindow(vexpand=True,hexpand=True,vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.expense_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,homogeneous=False,vexpand=True,hexpand=True)
        self.stack.add_titled(self.expense_scrolledwindow, "page1", "expense")
        # self.expense_scrolledwindow.set_child(self.expense_box)


        self.income_scrolledwindow=Gtk.ScrolledWindow(vexpand=True,hexpand=True,vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.income_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,homogeneous=False,vexpand=True,hexpand=True)
        self.stack.add_titled(self.income_scrolledwindow, "page2", "income")
        # self.income_scrolledwindow.set_child(self.income_box)

        # 建立 StackSwitcher 並連結到 Stack
        switcher = Gtk.StackSwitcher(name="switcher")
        switcher.set_stack(self.stack)

        # 將 Switcher 和 Stack 添加到主容器
        self.up_box.append(switcher)
        self.down_box.append(self.stack)

        self.token=TokenHandler().load_token_encrypted()
        print(self.token)

        self.create_btn()
        self.item=["expense","income"]

        self.show()
        

    def create_btn(self):
        self.income_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,homogeneous=False,vexpand=True,hexpand=True)
        self.expense_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,homogeneous=False,vexpand=True,hexpand=True)
        self.type_jason=CategoryHandler.get_all_categories(token=self.token)
        for i in self.type_jason:
            if(i['category_type']=="expense"):
                button=Gtk.Button(hexpand=True,label=i['name'],css_classes=['button'])
                self.expense_box.append(button)
            elif(i['category_type']=="income"):
                button=Gtk.Button(hexpand=True,label=i['name'],css_classes=['button'])
                self.income_box.append(button)
            button.connect("clicked",self.on_button_clicked)
        button=Gtk.Button(hexpand=True,label="+",css_classes=['button'])
        self.income_box.append(button)
        button.connect("clicked",self.add_category)
        button=Gtk.Button(hexpand=True,label="+",css_classes=['button'])
        self.expense_box.append(button)
        button.connect("clicked",self.add_category)
        self.income_scrolledwindow.set_child(self.income_box)
        self.expense_scrolledwindow.set_child(self.expense_box)




    def on_button_clicked(self, button):
        # 按下按鈕後，建立新視窗

        button=cast(Gtk.Button,button)
        new_window = Gtk.Window(title="revise")
        new_window.set_default_size(300, 400)

        bottom_box=Gtk.Box(hexpand=True,vexpand=True,orientation=Gtk.Orientation.VERTICAL,name="background",spacing=10)
        new_window.set_child(bottom_box)
        name_label=Gtk.Label(label="Name",css_classes=["label"])
        name_entry=Gtk.Entry(text=button.get_label(),css_classes=["entry"],name="name_entry")
        type_label=Gtk.Label(label="Type",css_classes=["label"])
        
        type_dropdown=Gtk.DropDown.new_from_strings(self.item)
        type_dropdown.set_name("dropbox")
        if(self.stack.get_visible_child_name()=="page1"):
            type_dropdown.set_selected(0)
        else:
            type_dropdown.set_selected(1)
        update_button=Gtk.Button(label="update",css_classes=['c_button'])
        delete_button=Gtk.Button(label="delete",css_classes=['c_button'])

        bottom_box.append(name_label)
        bottom_box.append(name_entry)
        bottom_box.append(type_label)
        bottom_box.append(type_dropdown)
        bottom_box.append(update_button)
        bottom_box.append(delete_button)

        self.str_1=button.get_label()
        self.type=self.item[type_dropdown.get_selected()]

        self.btn_box_dict={}
        self.btn_box_dict[update_button]=bottom_box

        update_button.connect("clicked",self.update)
        update_button.connect_after("clicked", lambda btn: new_window.close())

        delete_button.connect("clicked",self.delete)
        delete_button.connect_after("clicked", lambda btn: new_window.close())

        
        new_window.show()

    def update(self,button):
        id=0
        name_text=""
        s_type=""
        for i in self.type_jason:
            if(i['name']==self.str_1 and i['category_type']==self.type):
                id=i['id']
                break
        child = self.btn_box_dict.get(button).get_first_child()
        while child:
            if child.get_name() == "name_entry":
                print(1)
                child=cast(Gtk.Entry,child)
                name_text=child.get_text()
            elif child.get_name() == "dropbox":
                index=child.get_selected()
                s_type=self.item[index]
            child = child.get_next_sibling()

        CategoryHandler.update_category(self.token,id,name_text,s_type)
        self.create_btn()
        self.btn_box_dict.pop(button)

    def delete(self,button):
        id=0
        for i in self.type_jason:
            if(i['name']==self.str_1 and i['category_type']==self.type):
                id=i['id']
                break
        CategoryHandler.delete_category(self.token,id)
        self.create_btn()

    def add_category(self,button):
        button=cast(Gtk.Button,button)
        new_window = Gtk.Window(title="ADD")
        new_window.set_default_size(300, 400)

        bottom_box=Gtk.Box(hexpand=True,vexpand=True,orientation=Gtk.Orientation.VERTICAL,name="background",spacing=10)
        new_window.set_child(bottom_box)
        name_label=Gtk.Label(label="Name",css_classes=["label"])
        name_entry=Gtk.Entry(name="name_entry",css_classes=["entry"])
        
        if(self.stack.get_visible_child_name()=="page1"):
            self.str_2="expense"
        else:
            self.str_2="income"
        add_button=Gtk.Button(label="ADD",css_classes=['c_button'])

        bottom_box.append(name_label)
        bottom_box.append(name_entry)
        bottom_box.append(add_button)

        self.btn_box_dict={}
        self.btn_box_dict[add_button]=name_entry

        add_button.connect("clicked",self.add_btn_clicked)
        add_button.connect_after("clicked", lambda btn: new_window.close())

        
        new_window.show()

    def add_btn_clicked(self,button):
        entry=self.btn_box_dict.get(button)
        entry=cast(Gtk.Entry,entry)
        print(self.str_2)
        print(entry.get_text())
        CategoryHandler.create_category(self.token,entry.get_text(),self.str_2)
        self.btn_box_dict.pop(button)
        self.str_2=""
        self.create_btn()
