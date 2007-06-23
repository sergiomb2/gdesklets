from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigButton(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__initialized = False

        ConfigWidget.__init__(self, name, getter, setter, caller)


    def update(self): pass


    def get_widgets(self):

        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        self.__button = gtk.Button("")
        self.__button.show()
        self.__button.connect("clicked", self.__on_click)
        align.add(self.__button)

        return (align,)


    def __on_click(self, src):

        self.call_callback()


    def _set_label(self, value): self.__button.set_label(value)
    def _set_enabled(self, value): self.__button.set_sensitive(value)
