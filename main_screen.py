import gi
import calendar
import datetime
import os

from AccountingPage import AccountingPage
from Type_Adjusting import TypeAdjusting

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, GLib
from api_reference import TokenHandler,ExpenseHandler,CategoryHandler,UserAuthHandler
from typing import cast

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self,main_window,stack):
        super().__init__()

        self.stack = stack
        self.now=datetime.datetime.now()
        self.now_month=self.now.month
        self.now_year=self.now.year


        self.select_year,self.select_month,self.select_day=self.now.year,self.now.month,self.now.day

        self.now_month_start,self.now_month_days=calendar.monthrange(self.now_year,self.now_month)

        # self.set_default_size(1600,900)
        main_window.set_size_request(1000,800)

        self.bottom_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,homogeneous=True)
        self.bottom_box.set_vexpand(True)
        self.bottom_box.set_hexpand(True)
        self.bottom_box.set_name("background")
        main_window.append(self.bottom_box)

        self.left_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.left_box.set_vexpand(True)
        self.left_box.set_hexpand(True)
        self.left_box.set_name("main_box")
        self.left_box.set_orientation(orientation=Gtk.Orientation.VERTICAL)

        self.right_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.right_box.set_vexpand(True)
        self.right_box.set_hexpand(True)
        self.right_box.set_name("main_box")
        self.right_box.set_orientation(orientation=Gtk.Orientation.VERTICAL)

        self.bottom_box.append(self.left_box)
        self.bottom_box.append(self.right_box)

        #left box
        self.y_m_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.y_m_box.set_name("label_box")
        self.y_m_box.set_halign(Gtk.Align.FILL)
        self.left_box.append(self.y_m_box)

        self.y_m_label=Gtk.Label.new(f"{self.now.year}/{self.now.month}")
        self.y_m_label.set_name("label")
        self.y_m_label.set_halign(Gtk.Align.CENTER)
        self.y_m_box.append(self.y_m_label)

        self.clander_container=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.clander_container.set_css_classes(["container"])
        self.left_box.append(self.clander_container)

        self.last_month=Gtk.Button()
        self.last_month.set_label("◀")
        self.last_month.set_valign(Gtk.Align.CENTER)
        self.last_month.set_name("clander_button")
        self.clander_container.append(self.last_month)

        self.clander=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.clander.set_vexpand(True)
        self.clander.set_hexpand(True)
        self.clander_container.append(self.clander)

        self.next_month=Gtk.Button()
        self.next_month.set_label("▶")
        self.next_month.set_valign(Gtk.Align.CENTER)
        self.next_month.set_name("clander_button")
        self.clander_container.append(self.next_month)

        self.grid=Gtk.Grid()
        self.grid.set_valign(Gtk.Align.FILL)
        self.grid.set_halign(Gtk.Align.FILL)
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)
        self.clander.append(self.grid)
        rows,cols=7,7
        for i in range(rows):
            for j in range(cols):
                if(i==0):
                    if(j==0):
                        label=Gtk.Label.new("SUN.")
                    if(j==1):
                        label=Gtk.Label.new("MON.")
                    if(j==2):
                        label=Gtk.Label.new("TUE.")
                    if(j==3):
                        label=Gtk.Label.new("WED.")
                    if(j==4):
                        label=Gtk.Label.new("TUS.")
                    if(j==5):
                        label=Gtk.Label.new("FRI.")
                    if(j==6):
                        label=Gtk.Label.new("SAT.")
                    label.set_name("calender_object_label")
                    label.set_vexpand(True)
                    label.set_hexpand(True)
                    self.grid.attach(label,j,i,1,1)
                    continue
                button_grid = Gtk.Button()
                button_grid.connect("clicked",self.f_select)
                button_grid.set_vexpand(True)
                button_grid.set_hexpand(True)
                button_grid.set_name("calender_object_button")
                self.grid.attach(button_grid, j, i, 1, 1)
        self.f_SetGrid()

        #right box
        self.r_date_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.r_date_box.set_name("label_box")
        self.r_date_box.set_hexpand(True)
        self.right_box.append(self.r_date_box)

        self.date_label=Gtk.Label()
        self.date_label.set_label(f"{self.select_year}/{self.select_month}/{self.select_day}")
        self.date_label.set_name("label")
        self.r_date_box.append(self.date_label)

        self.scrollwindow_container=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.scrollwindow_container.set_vexpand(True)
        self.scrollwindow_container.set_hexpand(True)
        self.scrollwindow_container.set_css_classes(["container"])
        self.right_box.append(self.scrollwindow_container)

        self.layout_scrollwindow=Gtk.ScrolledWindow()
        self.layout_scrollwindow.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        self.scrollwindow_container.append(self.layout_scrollwindow)

        self.layout=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.layout.set_vexpand(True)
        self.layout.set_hexpand(True)
        self.layout_scrollwindow.set_child(self.layout)

        box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=5,halign=Gtk.Align.END)
        self.show_revealer_btn=Gtk.Button(label="◀",css_classes=['button'])

        self.revealer=Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.btn_container=Gtk.Box(valign=Gtk.Align.END,halign=Gtk.Align.END,orientation=Gtk.Orientation.HORIZONTAL,spacing=10)
        self.revealer.set_child(self.btn_container)

        self.add_layout=Gtk.Button()
        self.add_layout.set_name("button")
        self.add_layout.set_label("+")
        self.add_layout.set_size_request(80,80)
        self.add_layout.connect("clicked",self.add)

        self.logout_btn=Gtk.Button(label="logout",css_classes=['button'])

        self.revise_btn=Gtk.Button(label="revise type",css_classes=['button'])

        self.btn_container.append(self.logout_btn)
        self.btn_container.append(self.revise_btn)
        self.btn_container.append(self.add_layout)

        box.append(self.show_revealer_btn)
        box.append(self.revealer)

        self.scrollwindow_container.append(box)

        self.next_month.connect("clicked",self.f_NextMonth)
        self.last_month.connect("clicked",self.f_LastMonth)
        self.show_revealer_btn.connect("clicked",self.show_revealer)
        self.revise_btn.connect("clicked",self.f_type_adjusting)
        self.logout_btn.connect("clicked",self.f_logout)

        date={"start_date":f"{self.select_year}-{self.select_month}-{self.select_day}",
              "end_date":f"{self.select_year}-{self.select_month}-{self.select_day}"}
        self.token=TokenHandler().load_token_encrypted()

        get_jason=ExpenseHandler.get_expense(token=self.token,id=None,params=date)

        type_jason=CategoryHandler.get_all_categories(token=self.token)

        self.array = [[] for _ in range(max(item["id"] for item in type_jason)+1)]

        self.delete_widget_dict={}
        self.c_delete_widget_dict={}
        self.expand_widget_dict={}
        self.box_store_dict={}

        for i in get_jason:
            pass
            S_data=C_data(i['id'],i['transaction_type'],i['category'],i['amount'],i['discount'],i['description'],i['store'],i['time'],i['detail'])
            self.array[int(i['category'])].append(S_data)

        for sublist in self.array:
            i=0
            sum=0
            for regis in sublist:
                regis=cast(C_data,regis)
                sum+=float(regis.amount)
                category=regis.category
            if(sublist!=[]):
                category_json=CategoryHandler.get_category(self.token,category)
                contain_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,hexpand=True,css_classes=["contain_box"],name=category_json['name'])
                self.box_store_dict[category_json['name']]=0
                h1_contain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="uh_1_box")
                h2_contain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="uh_2_box")
                label_category=Gtk.Label(label=category_json['name']+"                 ",css_classes=["label"])
                label_sum=Gtk.Label(label=" "+str(sum)+" NT$",css_classes=["label"],name="sum")
                expand_button=Gtk.Button(label="◀",css_classes=["label"])
                space_box=Gtk.Box(hexpand=True)
                revealer=Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN)
                h1_contain_box.append(label_category)
                h1_contain_box.append(label_sum)
                h1_contain_box.append(space_box)
                h1_contain_box.append(expand_button)
                h2_contain_box.append(revealer)
                contain_box.append(h1_contain_box)
                contain_box.append(h2_contain_box)
                self.layout.append(contain_box)
                self.expand_widget_dict[expand_button]=revealer
                revealer_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,hexpand=True)
                revealer.set_child(revealer_box)
                expand_button.connect("clicked",self.expand_revelar)
                for regis in sublist:
                    incontain_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,hexpand=True)
                    h1_incontain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="h1_box",homogeneous=False)
                    h2_incontain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="h2_box",homogeneous=False)
                    description_label=Gtk.Label(label=regis.description,css_classes=["label"],name="description")
                    amount_label=Gtk.Label(label=str(regis.amount)+"NT$",css_classes=["label"],name="amount")
                    store_label=Gtk.Label(label=regis.store,css_classes=["label"])
                    detail_label=Gtk.Label(label=str(regis.detail),css_classes=["label"],name="detail")
                    time_label=Gtk.Label(label=str(regis.time),css_classes=["label"],name="time")
                    delete_button=Gtk.Button(label="🗑️",css_classes=["label"])
                    edit_button=Gtk.Button(label="✎ ",css_classes=["label"])
                    edit_button.set_margin_end(5)
                    space_box=Gtk.Box(hexpand=True)
                    h1_incontain_box.append(store_label)
                    h1_incontain_box.append(space_box)

                    space_box=Gtk.Box(hexpand=True)
                    h1_incontain_box.append(amount_label)
                    h1_incontain_box.append(space_box)

                    space_box=Gtk.Box(hexpand=True)
                    h1_incontain_box.append(description_label)
                    h1_incontain_box.append(space_box)

                    h1_incontain_box.append(edit_button)
                    h1_incontain_box.append(delete_button)

                    space_box=Gtk.Box(hexpand=True)
                    h2_incontain_box.append(detail_label)
                    h2_incontain_box.append(space_box)
                    h2_incontain_box.append(time_label)

                    incontain_box.append(h1_incontain_box)
                    incontain_box.append(h2_incontain_box)

                    divider = Gtk.Box(hexpand=True)
                    divider.set_size_request(-1,2)
                    divider.set_margin_bottom(5)
                    divider.set_name("Divider")
                    incontain_box.append(divider)

                    revealer_box.append(incontain_box)
                    self.delete_widget_dict[delete_button]=incontain_box
                    self.delete_widget_dict[edit_button]=incontain_box
                    delete_button.connect("clicked",self.delete_widget)
                    edit_button.connect("clicked",self.edit_widget)
                    self.c_delete_widget_dict[delete_button]=category_json['name']
                    self.c_delete_widget_dict[edit_button]=category_json['name']
                    self.box_store_dict[category_json['name']]+=1

    def f_NextMonth(self,button):
        self.now_month+=1
        if(self.now_month>12):
            self.now_month=1
            self.now_year+=1
        self.y_m_label.set_label(f"{self.now_year}/{self.now_month}")
        self.now_month_start,self.now_month_days=calendar.monthrange(self.now_year,self.now_month)
        self.f_SetGrid()

    def f_LastMonth(self,button):
        self.now_month-=1
        if(self.now_month<1):
            self.now_month=12
            self.now_year-=1
        self.y_m_label.set_label(f"{self.now_year}/{self.now_month}")
        self.now_month_start,self.now_month_days=calendar.monthrange(self.now_year,self.now_month)
        self.f_SetGrid()

    def f_select(self,button):
        for i in range(1,7):
            for j in range(0,7):
                child=self.grid.get_child_at(j,i)
                if isinstance(child, Gtk.Button):
                    child.set_name("calender_object_button")
        button.set_name("selected")
        self.select_year=self.now_year
        self.select_month=self.now_month
        self.select_day=int(button.get_label())
        self.date_label.set_label(f"{self.select_year}/{self.select_month}/{self.select_day}")
        self.creat_widget()

    def f_SetGrid(self):
        for i in range(1,7):
            for j in range(0,7):
                child=self.grid.get_child_at(j,i)
                child.set_name("calender_object_button")
                child.set_visible(False)
                child.set_sensitive(True)
                child.set_opacity(1)
        #清除被選中的效果

        last_month=self.now_month-1
        last_year=self.now_year
        if(last_month<1):
            last_month=12
            last_year-=1
        last_year=self.now_year
        if(last_month>12):
            last_month=1
            last_year+=1

        a,last_month_day=calendar.monthrange(last_year,last_month)
        begin=last_month_day-(self.now_month_start+1)%7+1
        a=1

        counter=1
        for i in range(1,7):
            if(i==1):
                for j in range(0,7):
                    child=self.grid.get_child_at(j,i)
                    if(j>=(self.now_month_start+1)%7):
                        child.set_label(str(counter))
                        child.set_visible(True)
                        counter+=1
                        if(self.select_year==self.now_year and self.select_month==self.now_month):
                            if(int(child.get_label())==self.select_day):
                                child.set_name("selected")
                    else:
                        child.set_label(str(begin))
                        begin+=1
                        child.set_visible(True)
                        child.set_sensitive(False)
                        child.set_opacity(0.5)
            else:
                if(counter>self.now_month_days):
                    break
                for j in range(0,7):
                    child=self.grid.get_child_at(j,i)
                    child.set_label(str(counter))
                    child.set_visible(True)
                    if(self.select_year==self.now_year and self.select_month==self.now_month):
                        if(int(child.get_label())==self.select_day):
                            child.set_name("selected")
                    if(counter>self.now_month_days):
                        child.set_label(str(a))
                        a+=1
                        child.set_sensitive(False)
                        child.set_visible(True)
                        child.set_opacity(0.5)
                    counter+=1
        #生成日歷

    def expand_revelar(self,button):
        revealer=self.expand_widget_dict.get(button)
        revealer=cast(Gtk.Revealer,revealer)
        button=cast(Gtk.Button,button)
        flag=revealer.get_reveal_child()
        revealer.set_reveal_child(not flag)
        if(flag==True):
            button.set_label("◀")
        else:
            button.set_label("▼")

    def delete_widget(self,button):
        deleted_box=self.delete_widget_dict.get(button)
        deleted_box=cast(Gtk.Box,deleted_box)
        child = deleted_box.get_first_child()
        divider = None
        while child:
            if child.get_name() == "h1_box":
                h1_box=child
                h1_box=cast(Gtk.Box,h1_box)
            elif child.get_name() == "h2_box":
                h2_box=child
                h2_box=cast(Gtk.Box,h2_box)
            elif child.get_name() == "Divider":
                divider=child
                divider=cast(Gtk.Box,divider)
            child = child.get_next_sibling()

        child = h1_box.get_first_child()
        while child:
            if child.get_name() == "description":
                description=child
                description=(description.get_label())
            elif child.get_name() == "amount":
                amount=child
                amount=(amount.get_label())
            child = child.get_next_sibling()
        child = h2_box.get_first_child()
        while child:
            if child.get_name() == "time":
                s_time=child
                s_time=(s_time.get_label())
            if child.get_name() == "detail":
                detail = child
                detail = (detail.get_label())
            child = child.get_next_sibling()
        str_len=0
        for i in amount:
            if(i!="N"):
                str_len+=1
            else:
                break
        amount=str(amount)[:str_len]
        print(amount)

        flag=0
        for uplist in self.array:
            if(flag==1):
                break
            for sublist in uplist:
                regis=cast(C_data,sublist)
                if regis.description==description and regis.time==s_time and regis.amount==amount and str(regis.detail) == str(detail):
                    flag=1
                    category_json=CategoryHandler.get_category(self.token,regis.category)
                    break
        self.array[category_json['id']].remove(regis)
        ExpenseHandler.delete_expense(self.token,regis.id)
        deleted_box.remove(h1_box)
        deleted_box.remove(h2_box)
        if divider:
            deleted_box.remove(divider)
        self.box_store_dict[category_json['name']]-=1
        if(self.box_store_dict[category_json['name']]==0):
            child = self.layout.get_first_child()
            while child:
                if child.get_name() == category_json['name']:
                    self.layout.remove(child)
                    break
                child = child.get_next_sibling()
        else:
            child = self.layout.get_first_child()
            while child:
                if child.get_name() == category_json['name']:
                    contain_box=child
                    contain_box=cast(Gtk.Box,contain_box)
                    break
                child = child.get_next_sibling()
            child = contain_box.get_first_child()
            while child:
                if child.get_name() == "uh_1_box":
                    h1_box=child
                    h1_box=cast(Gtk.Box,h1_box)
                    break
                child = child.get_next_sibling()
            child = h1_box.get_first_child()
            while child:
                if child.get_name() == "sum":
                    sum_label=child
                    sum_label=cast(Gtk.Label,sum_label)
                    break
                child = child.get_next_sibling()
            sum=0
            for sublist in self.array[category_json['id']]:
                regis=cast(C_data,sublist)
                sum+=float(regis.amount)
            sum_label.set_label(" "+str(sum)+" NT$")
            print(sum)

    def edit_widget(self,button):
        deleted_box=self.delete_widget_dict.get(button)
        deleted_box=cast(Gtk.Box,deleted_box)
        child = deleted_box.get_first_child()
        divider = None
        while child:
            if child.get_name() == "h1_box":
                h1_box=child
                h1_box=cast(Gtk.Box,h1_box)
            elif child.get_name() == "h2_box":
                h2_box=child
                h2_box=cast(Gtk.Box,h2_box)
            elif child.get_name() == "Divider":
                divider=child
                divider=cast(Gtk.Box,divider)
            child = child.get_next_sibling()

        child = h1_box.get_first_child()
        while child:
            if child.get_name() == "description":
                description=child
                description=(description.get_label())
            elif child.get_name() == "amount":
                amount=child
                amount=(amount.get_label())
            child = child.get_next_sibling()
        child = h2_box.get_first_child()
        while child:
            if child.get_name() == "time":
                s_time=child
                s_time=(s_time.get_label())
            if child.get_name() == "detail":
                detail = child
                detail = (detail.get_label())
            child = child.get_next_sibling()
        str_len=0
        for i in amount:
            if(i!="N"):
                str_len+=1
            else:
                break
        amount=str(amount)[:str_len]
        print(amount)

        flag=0
        for uplist in self.array:
            if(flag==1):
                break
            for sublist in uplist:
                regis=cast(C_data,sublist)
                if regis.description==description and regis.time==s_time and regis.amount==amount and str(regis.detail) == str(detail):
                    flag=1
                    category_json=CategoryHandler.get_category(self.token,regis.category)
                    break

        accounting_box = Gtk.Box()
        self.stack.add_named(accounting_box, "AccountingPage")
        self.stack.set_visible_child_name("AccountingPage")
        accounting_page = AccountingPage(accounting_box,date=f"{self.select_year}-{self.select_month}-{self.select_day}",id=regis.id,stack=self.stack)

        GLib.idle_add(self.accounting_thread,accounting_page)

    def accounting_thread(self,accounting_page):
        if accounting_page.status == 0:
            return True
        if accounting_page.status == 1:
            GLib.idle_add(self.creat_widget)
        return False

    def creat_widget(self):
        self.layout=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,vexpand=True,hexpand=True)
        self.layout_scrollwindow.set_child(self.layout)
        date={"start_date":f"{self.select_year}-{self.select_month}-{self.select_day}",
              "end_date":f"{self.select_year}-{self.select_month}-{self.select_day}"}
        self.token=TokenHandler().load_token_encrypted()
        get_jason=ExpenseHandler.get_expense(token=self.token,id=None,params=date)

        type_jason=CategoryHandler.get_all_categories(token=self.token)

        self.array = [[] for _ in range(max(item["id"] for item in type_jason)+1)]

        self.delete_widget_dict={}
        self.c_delete_widget_dict={}
        self.expand_widget_dict={}
        self.box_store_dict={}
        for i in get_jason:
            k=0
            time_len=0
            for j in i['time']:
                if(j==":"):
                    k+=1
                if(k==2):
                    break
                time_len+=1
            s_time=str(i['time'])[:time_len]
            S_data=C_data(i['id'],i['transaction_type'],i['category'],i['amount'],i['discount'],i['description'],i['store'],i['time'],i['detail'])
            self.array[int(i['category'])].append(S_data)

        for sublist in self.array:
            i=0
            sum=0
            for regis in sublist:
                regis=cast(C_data,regis)
                sum+=float(regis.amount)
                category=regis.category
            if(sublist!=[]):
                category_json=CategoryHandler.get_category(self.token,category)
                contain_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,hexpand=True,css_classes=["contain_box"],name=category_json['name'])
                self.box_store_dict[category_json['name']]=0
                h1_contain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="uh_1_box")
                h2_contain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="uh_2_box")
                label_category=Gtk.Label(label=category_json['name']+"                 ",css_classes=["label"])
                label_sum=Gtk.Label(label=" "+str(sum)+" NT$",css_classes=["label"],name="sum")
                expand_button=Gtk.Button(label="◀",css_classes=["label"])
                space_box=Gtk.Box(hexpand=True)
                revealer=Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN)
                h1_contain_box.append(label_category)
                h1_contain_box.append(label_sum)
                h1_contain_box.append(space_box)
                h1_contain_box.append(expand_button)
                h2_contain_box.append(revealer)
                contain_box.append(h1_contain_box)
                contain_box.append(h2_contain_box)
                self.layout.append(contain_box)
                self.expand_widget_dict[expand_button]=revealer
                revealer_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,hexpand=True)
                revealer.set_child(revealer_box)
                expand_button.connect("clicked",self.expand_revelar)
                for regis in sublist:
                    incontain_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,hexpand=True)
                    h1_incontain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="h1_box",homogeneous=False)
                    h2_incontain_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True,name="h2_box",homogeneous=False)
                    description_label=Gtk.Label(label=regis.description,css_classes=["label"],name="description")
                    amount_label=Gtk.Label(label=str(regis.amount)+"NT$",css_classes=["label"],name="amount")
                    store_label=Gtk.Label(label=regis.store,css_classes=["label"])
                    detail_label=Gtk.Label(label=str(regis.detail),css_classes=["label"],name="detail")
                    time_label=Gtk.Label(label=str(regis.time),css_classes=["label"],name="time")
                    delete_button=Gtk.Button(label="🗑️",css_classes=["label"])
                    edit_button=Gtk.Button(label="✎ ",css_classes=["label"])
                    edit_button.set_margin_end(5)
                    space_box=Gtk.Box(hexpand=True)
                    h1_incontain_box.append(store_label)
                    h1_incontain_box.append(space_box)

                    space_box=Gtk.Box(hexpand=True)
                    h1_incontain_box.append(amount_label)
                    h1_incontain_box.append(space_box)

                    space_box=Gtk.Box(hexpand=True)
                    h1_incontain_box.append(description_label)
                    h1_incontain_box.append(space_box)

                    h1_incontain_box.append(edit_button)
                    h1_incontain_box.append(delete_button)

                    space_box=Gtk.Box(hexpand=True)



                    h2_incontain_box.append(detail_label)
                    h2_incontain_box.append(space_box)
                    h2_incontain_box.append(time_label)
                    incontain_box.append(h1_incontain_box)
                    incontain_box.append(h2_incontain_box)

                    divider = Gtk.Box(hexpand=True)
                    divider.set_size_request(-1,2)
                    divider.set_margin_bottom(5)
                    divider.set_name("Divider")
                    incontain_box.append(divider)
                    revealer_box.append(incontain_box)
                    self.delete_widget_dict[delete_button]=incontain_box
                    self.delete_widget_dict[edit_button]=incontain_box
                    delete_button.connect("clicked",self.delete_widget)
                    edit_button.connect("clicked",self.edit_widget)
                    self.c_delete_widget_dict[delete_button]=category_json['name']
                    self.c_delete_widget_dict[edit_button]=category_json['name']
                    self.box_store_dict[category_json['name']]+=1
        return False

    def add(self,button):
        accounting_box = Gtk.Box()
        self.stack.add_named(accounting_box, "AccountingPage")
        self.stack.set_visible_child_name("AccountingPage")
        accounting_page = AccountingPage(accounting_box,date=f"{self.select_year}-{self.select_month}-{self.select_day}",id=None,stack=self.stack)

        GLib.idle_add(self.accounting_thread,accounting_page)

    def show_revealer(self,button):
        is_visible = self.revealer.get_reveal_child()
        self.revealer.set_reveal_child(not is_visible)
        if(is_visible==True):
            button.set_label("◀")
        else:
            button.set_label("▶")

    def f_type_adjusting(self,button):
        TypeAdjusting()

    def f_logout(self,button):
        UserAuthHandler.logout(self.token)
        self.stack.remove(self.stack.get_child_by_name("MainWindow"))
        self.stack.set_visible_child_name("ThirdLogin")
        # self.stack.get_child_by_name("ThirdLogin").set_size_request(700, 500)
        print("SUCCESS")
        os.remove("token.enc")


class C_data:
    def __init__(self, id, transaction_type,category,amount,discount,description,store,time,detail):
        self.id=id
        self.transaction_type=transaction_type
        self.category=category
        self.amount=amount
        self.discount=discount
        self.description=description
        self.store=store
        self.time=time
        self.detail=detail
