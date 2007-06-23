from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigFont(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, False, doc = "Font description")


    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        self.__btn = gtk.FontButton()
        self.__btn.set_use_font(True)
        self.__btn.set_use_size(False)
        self.__btn.set_show_style(True)
        self.__btn.set_show_size(True)
        self.__btn.show()
        self.__btn.connect("font-set", self.__on_change)

        return (align, self.__btn)


    def __on_change(self, src):

        value = src.get_font_name()
        self._set_config(value)


    def _set_enabled(self, value): self.__btn.set_sensitive(value)
    def _set_label(self, value): self.__label.set_text(value)

    def _setp_value(self, key, value):

        self.__btn.set_font_name(value)

        # force "font-set" signal
        self.__btn.emit("font-set")
        
        self._setp(key, value)
        
