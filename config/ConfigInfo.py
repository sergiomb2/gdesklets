from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk

class ConfigInfo(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_ANY, self._setp_value,
                                self._getp, "", doc = "Value")
        self._register_property("wrap", TYPE_BOOL, self._setp_wrap,
                                self._getp, "True", doc = "Whether to wrap the text")



    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        self.__info = gtk.Label("")
        self.__info.show()
        self.__info.set_line_wrap(True)
        self.__info.set_use_markup(True)
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        return (align, self.__info)


#    def __on_change(self, src, event):
#
#        value = src.get_text()
#        self._set_config(value)


    def _set_label(self, value): self.__label.set_markup(value)


    def _setp_value(self, key, value):

        self.__info.set_markup(value)
        self._set_config(value)
        self._setp(key, value)


    def _setp_wrap(self, key, value):

        self.__info.set_line_wrap(value)
        self._setp(key, value)
