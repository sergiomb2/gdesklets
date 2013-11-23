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
                                self._getp, -1,
                                doc = "Current selection index")

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, "",
                                doc = "Current selection")



    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
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

        if (self.__items_values) and (src.get_active() != -1):
            value = self.__items_values[src.get_active()]
            self._setp("selection", self.__optmenu.get_active())
            self._set_config(value)


    def _setp_items(self, key, items):

        old_selection = self.__optmenu.get_active()

        if old_selection != -1:
            old_key = self.__items_values[old_selection]

        self.__items_values = []
        self.__optmenu.get_model().clear()

        for v, k in items:
            self.__optmenu.append_text(v)
            self.__items_values.append(k)

        self._setp(key, items)

        if old_selection != -1:

            # if the old key is still present in the new items
            # list, we leave it as it is
            if old_key in self.__items_values:
                self.set_prop("value", old_key)

            # otherwise, if the items list contains at least one
            # element we selectt the last item
            # we could also select any other, e.g. the 0'th
            elif len(items) > 0:
                self.set_prop("value", self.__items_values[len(items)-1])

            # finally, if the list is empty we select
            # nothing at all
            else:
                self.__optmenu.set_active(-1)
                self._set_config("")
        elif len(items) > 0:
            self.set_prop("value", self.__items_values[len(items)-1])


    def _setp_selection(self, key, value):

        self.__optmenu.set_active(value)


    def _setp_value(self, key, value):
        old_value = self._getp("value")

        if value in self.__items_values:
            index = self.__items_values.index(value)
#            self.__optmenu.set_active(-1)  # make sure to get a change event
            self.__optmenu.set_active(index)
        else:
            value = ""
            self.__optmenu.set_active(-1)

        # produce a callback for changed value
        # in the bound variable, i.e. enum.value
        self._set_config(value)

        self._setp(key, value)

