from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk

class ConfigFloat(ConfigWidget):

    def __init__(self, name, getter, setter, caller, int_only = False):

        self.__int_only = int_only

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("min", TYPE_FLOAT, self._setp_lhd,
                                self._getp, 0.0, doc = "Lower bound")
        self._register_property("max", TYPE_FLOAT, self._setp_lhd,
                                self._getp, 9999.0, doc = "Upper bound")
        self._register_property("digits", TYPE_INT, self._setp_lhd,
                                self._getp, 2,
                                doc = "Numbers of decimal digits")
        self._register_property("increment", TYPE_FLOAT, self._setp_increment,
                                self._getp, 1, doc = "Size of increments")
        self._register_property("value", TYPE_FLOAT, self._setp_value,
                                self._getp, 0.0, doc = "Value")



    def get_widgets(self):

        low = self.get_prop("min")
        high = self.get_prop("max")
        digits = self.get_prop("digits")

        self.__label = gtk.Label("")
        self.__label.show()
        entry = gtk.Entry()
        entry.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        adjustment = gtk.Adjustment(0, low, high, 1, 1, 0)
        if (self.__int_only):
            self.__spin_button = gtk.SpinButton(adjustment, 1, 0)
        else:
            self.__spin_button = gtk.SpinButton(adjustment, 1, digits)
        self.__spin_button.set_numeric(True)
        self.__spin_button.show()

        self.__spin_button.connect("value-changed", self.__on_change)

        return (align, self.__spin_button)


    def __on_change(self, src):

        if (self.__int_only):
            value = src.get_value_as_int()
        else:
            value = src.get_value()
            
        self._set_config(value)


    def _set_enabled(self, value): self.__spin_button.set_sensitive(value)
    def _set_label(self, value): self.__label.set_text(value)


    def _setp_lhd(self, key, value):

        low, high = self.__spin_button.get_range()
        if (key == "min"):
            self.__spin_button.set_range(value, high)
        elif (key == "max"):
            self.__spin_button.set_range(low, value)
        elif (key == "digits"):
            self.__spin_button.set_digits(value)

        self._setp(key, value)


    def _setp_increment(self, key, value):

        self.__spin_button.set_increments(value, value * 10);
        self._setp(key, value)

    def _setp_value(self, key, value):

        self.__spin_button.set_value(value)
        self._setp(key, value)
