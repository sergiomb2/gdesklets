from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk

class ConfigString(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("password", TYPE_BOOL, self._setp_password,
                                self._getp, False,
                                doc = "Whether to obfuscate input")
        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, "", doc = "Value")




    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        self.__entry = gtk.Entry()
        self.__entry.set_width_chars(15)
        self.__entry.show()
        align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        self.__entry.set_invisible_char(unichr(0x2022))
        self.__entry.connect("focus-out-event", self.__on_change)

        return (align, self.__entry)


    def __on_change(self, src, event):

        value = src.get_text()
        self._set_config(value)


    def _set_enabled(self, value): self.__entry.set_sensitive(value)
    def _set_label(self, value): self.__label.set_text(value)


    def _setp_password(self, key, value):

        self.__entry.set_visibility(not value)
        self._setp(key, value)


    def _setp_value(self, key, value):

        self.__entry.set_text(value)
        self._set_config(value)
        self._setp(key, value)
