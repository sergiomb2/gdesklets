from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigColor(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, "black", doc = "Color value")


    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        self.__colorpicker = gtk.ColorButton()
        self.__colorpicker.set_use_alpha(True)
        self.__colorpicker.show()
        self.__colorpicker.connect("color-set", self.__on_change)

        return (align, self.__colorpicker)


    def _set_enabled(self, value):

        self.__colorpicker.set_sensitive(value)


    def _set_label(self, value):

        self.__label.set_text(value)



    def __on_change(self, src):

        color = src.get_color()
        alpha = src.get_alpha()
        value = "#%02X%02X%02X%02X" % (color.red >> 8, color.green >> 8,
                                       color.blue >> 8, alpha >> 8)
        self._set_config(value)


    def _setp_value(self, key, value):

        import utils
        r, g, b, alpha = utils.parse_color(value)
        self.__colorpicker.set_color(gtk.gdk.Color(r << 8, g << 8, b << 8))
        self.__colorpicker.set_alpha((alpha << 8) + alpha)
        self._set_config(value)
        self._setp(key, value)
