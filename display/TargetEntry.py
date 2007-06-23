from DisplayTarget import DisplayTarget
from utils.datatypes import *
from layout import Unit
from utils.Struct import Struct

import gobject
import gtk
import pango
import re


class TargetEntry(DisplayTarget):

    __ACTION_CHANGE = "change"

    # regular expression for parsing font description strings
    __RE_FONT = re.compile("(?P<name>.+?)"
                           "(?P<size>[0-9\.]+)"
                           "(?P<unit>[a-z]+)?$")


    def __init__(self, name, parent):

        DisplayTarget.__init__(self, name, parent)

        self.__widget = gtk.Entry()
        self.__widget.show()
        self.__widget.connect("changed", self.__on_changed)

        self._register_property("value", TYPE_STRING,
                                self._setp_value, self._getp)
        self._register_property("font", TYPE_STRING,
                                self._setp_font, self._getp)
        self._register_property("color", TYPE_STRING,
                                self._setp_color, self._getp)

        self._register_action(self.__ACTION_CHANGE)

        w, h = self.__widget.size_request()
        self.set_size(Unit.Unit(w, Unit.UNIT_PX), Unit.Unit(h, Unit.UNIT_PX))



    def get_widget(self): return self.__widget



    def __on_changed(self, src):

        self._setp("value", self.__widget.get_text())
        self._get_display().send_action(self, self.__ACTION_CHANGE, Struct())



    def _setp_font(self, key, value):

        if (not self.__widget.window):
            gobject.idle_add(self._setp_font, key, value)
            return

        m = re.match(self.__RE_FONT, value)
        if (m):
            name = m.group("name")
            unit = m.group("unit") or Unit.UNIT_PT
            size = m.group("size")
            if (size):
                unit = Unit.Unit(float(size), unit)
                size = unit.as_pt()
                value = "%s %f" % (name, size)

        fd = pango.FontDescription(value)
        self.__widget.modify_font(fd)

        # We need this hack to ensure that GTK resizes the widget after
        # having changed the font size.
        def f(self):
            w, h = self.__widget.size_request()
            self.set_size(Unit.Unit(w, Unit.UNIT_PX),
                          Unit.Unit(h, Unit.UNIT_PX))

        self.__widget.set_size_request(-1, -1)
        gobject.idle_add(f, self)
        self._setp(key, value)


    def _setp_color(self, key, value):

        self.__widget.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(value))

        self._setp(key, value)


    def _setp_value(self, key, value):

        self.__widget.set_text(value)
