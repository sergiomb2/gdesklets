from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigToggle(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__items_values = []

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("items", TYPE_LIST, self._setp_items,
                                self._getp, [],
                                doc = "List of (label, value) items")

        self._register_property("value", TYPE_LIST, self._setp_value,
                                self._getp, [],
                                doc = "Current selection")



    def get_widgets(self, items):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)
        self.__toggle = gtk.HBox(True, 6)
        self.__toggle.show()
     
        value = self._get_config()

        self.__buttons = []
        button = None
        for k, v in items:
           button = gtk.ToggleButton(k)
           button.show()
           button.connect("toggled", self.__on_change, v)
           self.__toggle.pack_start(button, True, True, 0)
           self.__buttons.append([button, v])
        return (align, self.__toggle)



    def _set_enabled(self, value):

        self.__toggle.set_sensitive(value)


    def _set_label(self, value):

        self.__label.set_text(value)
        

    def __on_change(self, src, value):

        selection = []
        if (self.__items_values):
           for b, v in self.__buttons:
               if (b.get_active()):
                  selection.append(v)
           self._setp("value", selection)
        self._set_config(selection)


    def _setp_items(self, key, items):

        self.__items_values = []
        for k, v in items:
            self.__items_values.append(v)
        #end for

        self._setp(key, items)
        self.set_prop("value", self.get_prop("value"))
        self._set_selection('value', self._getp('value'))


    def _set_selection(self, key, value):

        for button, button_value in self.__buttons:
           for v in value:
              if str(v) == str(button_value):
                 button.set_active(True)
             

    def _setp_value(self, key, value):

#        try:
#            index = self.__items_values.index(value)
#        except:
#            index = 0

        for button, button_value in self.__buttons:
            for v in value:
               if (v == button_value):
                  button.set_active(True)
        self._setp(key, value)

