from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigRadio(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__items_values = []

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("items", TYPE_LIST, self._setp_items,
                                self._getp, [],
                                doc = "List of (label, value) items")

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, "",
                                doc = "Current selection")



    def get_widgets(self, items):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)
        self.__radio = gtk.VBox(False, 6)
        self.__radio.show()
     
	self.__buttons = []
        value = self._get_config()
	button = None
        for k, v in items:
           button = gtk.RadioButton(button, k)
           button.show()
           button.connect("toggled", self.__on_change, v)
           self.__radio.pack_start(button, True, True, 0)
           self.__buttons.append([button, v])
        return (align, self.__radio)



    def _set_enabled(self, value):

        self.__radio.set_sensitive(value)


    def _set_label(self, value): self.__label.set_markup(value)
        

    def __on_change(self, src, val):

         self._set_config(val)


    def _setp_items(self, key, items):

        self.__items_values = []
        for k, v in items:
           self.__items_values.append(v)
        #end for

        self._setp(key, items)
        self.set_prop("value", self.get_prop("value"))


    def _setp_value(self, key, value):

        try:
            index = self.__items_values.index(value)
        except:
            index = 0

        for b, v in self.__buttons:
            if (v == value):
                b.set_active(True)
        self._setp(key, value)

