from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigEnum(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__items_values = []

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("items", TYPE_LIST, self._setp_items,
                                self._getp, [],
                                doc = "List of (label, value) items")

        self._register_property("selection", TYPE_INT, self._setp_selection,
                                self._getp, 0,
                                doc = "Current selection index")

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, "",
                                doc = "Current selection")



    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        value = self._get_config()
        self.__optmenu = gtk.combo_box_new_text()
        self.__optmenu.show()
        self.__optmenu.connect("changed", self.__on_change)
        
        return (align, self.__optmenu)



    def _set_enabled(self, value):

        self.__optmenu.set_sensitive(value)


    def _set_label(self, value):

        self.__label.set_text(value)
        

    def __on_change(self, src):

        if (self.__items_values):
            value = self.__items_values[src.get_active()]
            self._setp("selection", self.__optmenu.get_active())
            self._set_config(value)


    def _setp_items(self, key, items):

        self.__items_values = []
        self.__optmenu.get_model().clear()
        for k, v in items:
            self.__optmenu.append_text(k)
            self.__items_values.append(v)
        #end for

        self._setp(key, items)
        self.set_prop("value", self.get_prop("value"))


    def _setp_selection(self, key, value):

        self.__optmenu.set_active(value)
            

    def _setp_value(self, key, value):

        try:
            index = self.__items_values.index(value)
        except:
            index = 0

        self.__optmenu.set_active(-1)  # make sure to get a change event
        self.__optmenu.set_active(index)
        self._setp(key, value)
