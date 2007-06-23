from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigBoolean(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__initialized = False

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_BOOL, self._setp_value,
                                self._getp, False, doc = "Boolean value")


    def get_widgets(self):

        self.__check = gtk.CheckButton("")
        self.__check.show()
        self.__check.connect("toggled", self.__on_change)

        return (self.__check,)


    def __on_change(self, src):

        value = src.get_active()
        self._set_config(value)


    def _set_label(self, value): self.__check.set_label(value)
    def _set_enabled(self, value): self.__check.set_sensitive(value)


    def _setp_value(self, key, value):

        old_value = self._getp("value")
        self.__check.set_active(value)

        if (not self.__initialized and value == old_value):
            # force "toggled" signal
            self.__check.toggled()
        self.__initialized = True
            
        self._setp(key, value)

