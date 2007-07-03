from ConfigWidget import ConfigWidget
from utils.datatypes import *

from main import HOME
import os.path

import gtk
import time


class ConfigDate(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, False, doc = "Date description")
        self.__gdesklets_timestring = "%m/%d/%Y %H:%M:%S"


    def get_widgets(self):

        self.__value = ""
        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        self.__calendar_start(self)
        self.__btn = gtk.Button()
        self.__btn.connect("clicked", self.__calendar_show)
        self.__labelbox = self.__CalendarButton()
        self.__btn.add(self.__labelbox)
        self.__labelbox.show()
        self.__btn.show()
        return (align, self.__btn)


### This is some kind of gtk.CalendarButton
    def __CalendarButton(self):
        self.__labelbox = gtk.HBox(False, 0)
        self.__labelbox.set_border_width(2)
        vsep =  gtk.VSeparator()
        image = gtk.Image()        
        path2image = os.path.join(HOME, "data/calendar.png")
        image.set_from_file(path2image)

        # Create a label for the button
        self.__btn_label = gtk.Label()

        # Pack the pixmap and label into the box
        self.__labelbox.pack_start(self.__btn_label, True, True, 3)
        self.__labelbox.pack_start(vsep, False, False, 3)
        self.__labelbox.pack_start(image, False, False, 3)
        self.__btn_label.show()
	vsep.show()
        image.show()
        return self.__labelbox


    def __on_change(self):
        return


    def _set_enabled(self, value): self.__btn.set_sensitive(value)
    def _set_label(self, value): self.__label.set_text(value)

    def _setp_value(self, key, value):
        try:
             time.strptime(value, self.__gdesklets_timestring)
        except ValueError:
             value = self.__get_now()
        self.__value = value
        self._set_config(value)
        self._setp(key, value)
        self.__btn_label.set_label(value)


### A simple Calendar, (based on the MyCalendar from pygtk.org)
# (http://pygtk.org/pygtk2tutorial/sec-Calendar.html)

    def __calendar_show(self, src):
        self.newwindow.show_all()

    def __get_now(self):
        return time.strftime(self.__gdesklets_timestring, time.localtime())

    def __date_to_string(self, fulldate):
        return time.strftime(self.__gdesklets_timestring, time.localtime(fulldate))

    def __string_to_date(self, datestring):
        try:
            fulldate = time.strptime(datestring, self.__gdesklets_timestring)
        except ValueError:
            fulldate = time.strptime(self.__get_now(), self.__gdesklets_timestring)
        return fulldate


    def calendar_get_fulldate(self):
        year, month, day = self.calendar.get_date()
	hour = self.spinner_hour.get_value_as_int()
	minute = self.spinner_min.get_value_as_int()
	second = self.spinner_sec.get_value_as_int()
        mytime = time.mktime((year, month+1, day, hour, minute, second, 0, 0, -1))
        return mytime

    def calendar_set_info_strings(self, widget):
	self.new_date.set_text(self.__date_to_string(self.calendar_get_fulldate()))

    def calendar_day_selected(self, widget):
        self.__current_selection = self.calendar_get_fulldate()
        self.calendar_set_info_strings(self)

    def calendar_day_selected_double_click(self, widget):
        self.calendar_set_info_strings(self)

    def newwindow_hide(self, widget):
        self.newwindow.hide()

    def calendar_update_date(self, widget):
        self.__value = self.__date_to_string(self.calendar_get_fulldate())        
        self._setp_value("value", self.__value)
        self.newwindow.hide()

    def calendar_set_time(self, date):
        self.spinner_hour.set_value(date[3])
        self.spinner_min.set_value(date[4])
        self.spinner_sec.set_value(date[5])

    def calendar_goto_date(self, date):
        self.calendar.select_month(int(date[1]-1), int(date[0]))
	self.calendar_mark_selected_day(self, date)

    def calendar_reset_date(self, widget):
        self.calendar_goto_date(self.__string_to_date(self.__value))
        self.calendar_set_time(self.__string_to_date(self.__value))

    def calendar_now_date(self, widget):
        self.calendar_goto_date(self.__string_to_date(self.__get_now()))
        self.calendar_set_time(self.__string_to_date(self.__get_now()))


    def calendar_mark_selected_day(self, widget, date):
        self.calendar.clear_marks()
        year, month, day = self.calendar.get_date()
        if (year == date[0]) and (month == date[1]-1):
            self.calendar.mark_day(date[2])
            self.calendar.select_day(date[2])

    def __calendar_start(self, widget):
        self.DEF_PAD = 10
        self.DEF_PAD_SMALL = 5

        # self.__current_selction: time-tuple (9 elements) of the current selection
        self.__current_selection = self.__string_to_date(self.__value)

        self.calendar = None

        self.newwindow = gtk.Window()
        self.newwindow.set_title("Pick a date")
        self.newwindow.set_border_width(5)
        self.newwindow.set_destroy_with_parent(True)
        self.newwindow.connect("delete-event", self.newwindow.hide_on_delete)
        self.newwindow.set_resizable(False)

        vbox = gtk.VBox(False, self.DEF_PAD)
        self.newwindow.add(vbox)
        vbox.show()

        hbox = gtk.HBox(False, self.DEF_PAD)
        vbox.pack_start(hbox, True, True, self.DEF_PAD)
        hbbox = gtk.HButtonBox()
        hbox.pack_start(hbbox, False, False, self.DEF_PAD)
        hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        hbbox.set_spacing(5)
        hbox.show()
        hbbox.show()

# Calendar widget
        self.calendar = gtk.Calendar()
        hbbox.pack_start(self.calendar, False, True, self.DEF_PAD)
	self.calendar.set_display_options(11)
# 11 = gtk.CALENDAR_SHOW_HEADING, gtk.CALENDAR_SHOW_DAY_NAMES, gtk.CALENDAR_SHOW_WEEK_NUMBERS
        self.calendar.connect("month_changed", self.calendar_mark_selected_day, self.__current_selection)
        self.calendar.connect("day_selected", self.calendar_day_selected)
        self.calendar.connect("day_selected_double_click", self.calendar_day_selected)
        self.calendar.connect("prev_month", self.calendar_mark_selected_day, self.__current_selection)
        self.calendar.connect("next_month", self.calendar_mark_selected_day, self.__current_selection)
        self.calendar.connect("prev_year", self.calendar_mark_selected_day, self.__current_selection)
        self.calendar.connect("next_year", self.calendar_mark_selected_day, self.__current_selection)
        self.calendar.show()

# Day, month, year spinners
        hbox_time = gtk.HBox(True, 5)
        vbox.pack_start(hbox_time, True, True, 5)
        hbox_time.set_spacing(5)

        vbox_hour = gtk.VBox(False, 0)
        hbox_time.pack_start(vbox_hour, True, False, 5)

        label_hour = gtk.Label("Hour")
        label_hour.set_alignment(0.5, 0.5)
        vbox_hour.pack_start(label_hour, True, False, 0)

        adj_hour = gtk.Adjustment(0.0, 0.0, 23.0, 1.0, 5.0, 0.0)
        self.spinner_hour = gtk.SpinButton(adj_hour, 0, 0)
        self.spinner_hour.set_wrap(True)
        self.spinner_hour.connect("value-changed", self.calendar_set_info_strings)
        vbox_hour.pack_start(self.spinner_hour, False, False, 0)

        vbox_min = gtk.VBox(False, 0)
        hbox_time.pack_start(vbox_min, True, False, 5)

        label_min = gtk.Label("Minute")
        label_min.set_alignment(0.5, 0.5)
        vbox_min.pack_start(label_min, True, False, 0)

        adj_min = gtk.Adjustment(0.0, 0.0, 59.0, 1.0, 5.0, 0.0)
        self.spinner_min = gtk.SpinButton(adj_min, 0, 0)
        self.spinner_min.set_wrap(True)
        self.spinner_min.connect("value-changed", self.calendar_set_info_strings)
        vbox_min.pack_start(self.spinner_min, False, False, 0)

        vbox_sec = gtk.VBox(False, 0)
        hbox_time.pack_start(vbox_sec, True, False, 5)

        label_sec = gtk.Label("Second")
        label_sec.set_alignment(0.5, 0.5)
        vbox_sec.pack_start(label_sec, True, False, 0)

        adj_sec = gtk.Adjustment(0.0, 0.0, 59.0, 1.0, 5.0, 0.0)
        self.spinner_sec = gtk.SpinButton(adj_sec, 0, 0)
        self.spinner_sec.set_wrap(True)
        self.spinner_sec.connect("value-changed", self.calendar_set_info_strings)
        vbox_sec.pack_start(self.spinner_sec, False, False, 0)

        separator = gtk.HSeparator()
        vbox.pack_start(separator, False, True, 0)

#  The information box
        info_align = gtk.Alignment(0.50, 0.0, 0.0, 0.0)
        hbox_info = gtk.HBox(False, self.DEF_PAD_SMALL)
        vbox.pack_start(info_align, False, False, self.DEF_PAD)
        info_align.add(hbox_info)

        label_alignnew = gtk.Alignment(1.0, 0.0, 0.0, 0.0)
        label_alignold = gtk.Alignment(1.0, 0.0, 0.0, 0.0)
        vbox_label = gtk.VBox (False, 3)
        hbox_info.pack_start(vbox_label, False, False, 0)
        label_newdate = gtk.Label("New date: ")
        vbox_label.pack_start(label_alignnew, False, False, 0)
        label_alignnew.add(label_newdate)
        label_olddate = gtk.Label("Old date: ")
        vbox_label.pack_start(label_alignold, False, False, 0)
        label_alignold.add(label_olddate)

        label_alignnew2 = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        label_alignold2 = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        vbox_value = gtk.VBox (False, 3)
        hbox_info.pack_start(vbox_value, False, False, 0)
        self.new_date = gtk.Label(self.__value)
        vbox_value.pack_start(label_alignnew2, False, False, 0)
        label_alignnew2.add(self.new_date)
        self.old_date = gtk.Label(self.__value)
        vbox_value.pack_start(label_alignold2, False, False, 0)
        label_alignold2.add(self.old_date)

# The Set-Boxen (Set 'now' and Re-Set)
        bbox = gtk.HButtonBox ()
        vbox.pack_start(bbox, False, False, 0)
        bbox.set_layout(gtk.BUTTONBOX_SPREAD)

        okbutton = gtk.Button("Set 'now'")
        okbutton.connect("clicked", self.calendar_now_date)
        bbox.add(okbutton)
        okbutton.set_flags(gtk.CAN_DEFAULT)
        okbutton.grab_default()
        button = gtk.Button("Re-set")
        button.connect("clicked", self.calendar_reset_date)
        bbox.add(button)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()

        separator = gtk.HSeparator()
        vbox.pack_start(separator, False, True, 0)

# OK/Cancel
        ok_bbox = gtk.HButtonBox ()
        vbox.pack_start(ok_bbox, False, False, 0)
        ok_bbox.set_layout(gtk.BUTTONBOX_END)

        button = gtk.Button("Cancel")
        button.connect("clicked", self.newwindow_hide)
        ok_bbox.add(button)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()
        okbutton = gtk.Button("OK")
        okbutton.connect("clicked", self.calendar_update_date)
        ok_bbox.add(okbutton)
        okbutton.set_flags(gtk.CAN_DEFAULT)
        okbutton.grab_default()

        self.calendar_set_time(self.__current_selection)
        self.calendar_goto_date(self.__current_selection)
        self.newwindow.hide_all()
