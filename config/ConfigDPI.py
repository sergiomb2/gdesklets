from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk

class ConfigDPI(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_INT, self._setp_value,
                                self._getp, "", doc = "DPI value")


    def get_widgets(self):

        vbox = gtk.VBox(spacing = 3)
        vbox.show()

        hbox = gtk.HBox(spacing = 6)
        hbox.show()
        vbox.add(hbox)
        lbl = gtk.Label("dpi:")
        hbox.pack_start(lbl, False, False)

        spin = gtk.SpinButton()
        spin.show()
        spin.set_range(10, 500)
        spin.set_increments(1, 10)
        spin.set_digits(0)
        spin.connect("value-changed", self.__on_change)
        hbox.pack_start(spin, False, False)

        self.__line = gtk.Viewport()
        self.__line.show()
        self.__line.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("grey80"))
        hbox.pack_start(self.__line, False, False)

        lbl = gtk.Label("<--  5 cm  /  1.97\"  -->")
        lbl.show()
        lbl.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
        self.__line.add(lbl)

        self.__label = gtk.Label("")
        self.__label.show()
        vbox.add(self.__label)

        self.__box = vbox
        self.__spin = spin
        return (vbox,)


    def __on_change(self, src, *args):

        value = int(src.get_value())
        self.__set_line(value)
        self._set_config(value)


    def __set_line(self, dpi):

        width = int(5 * (1 / 2.54) * dpi)
        self.__line.set_size_request(width, 10)


    def _set_enabled(self, value): self.__box.set_sensitive(value)
    def _set_label(self, value): self.__label.set_markup(value)



    def _setp_value(self, key, value):

        self.__spin.set_value(value)
        self._setp(key, value)
