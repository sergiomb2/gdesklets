from ConfigWidget import ConfigWidget
from utils.datatypes import *
from utils import vfs

import gtk
import os

# the modifier keys, i.e. the keys which don't represent full keybindings on
# their own
_MODIFIERS = ("Alt_L",
              "Alt_R",
              "Control_L",
              "Control_R",
              "Escape",
              "Hyper_L",
              "Hyper_R",
              "Super_L",
              "Super_R",
              "Shift_L",
              "Shift_R")

class ConfigKeyBinding(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_LIST, self._setp_value,
                                self._getp, "", doc = "keycode and modifiers")


    def get_widgets(self):

        def f(src):
            if (src.get_active()):
                gtk.gdk.keyboard_grab(src.window)
                src.set_label("")

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        self.__button = gtk.ToggleButton("F12")
        self.__button.set_use_underline(False)
        self.__button.show()
        self.__button.connect("clicked", f)
        self.__button.connect("key-press-event", self.__on_change)

        return (align, self.__button)


    def __key2text(self, keycode, modifiers):

        keymap = gtk.gdk.keymap_get_default()
        keyval, nil, nil, nil = keymap.get_entries_for_keycode(keycode)[0]

        out = ""
        if (gtk.gdk.SHIFT_MASK & modifiers):
            out += "<Shift> "
        if (gtk.gdk.CONTROL_MASK & modifiers):
            out += "<Ctrl> "
        if (gtk.gdk.MOD1_MASK & modifiers):
            out += "<Alt> "

        if (out): out += "+ "
        out += "<" + gtk.gdk.keyval_name(keyval) + ">"

        return out


    def __on_change(self, src, event):

        if (src.get_active()):
            name = gtk.gdk.keyval_name(event.keyval)

            if (not name in _MODIFIERS):
                src.set_label(self.__key2text(event.hardware_keycode,
                                              event.state))
                gtk.gdk.keyboard_ungrab()
                src.set_active(False)
            
        self._set_config((event.hardware_keycode, int(event.state)))



    def _set_label(self, value): self.__label.set_text(value)
    def _set_enabled(self, value): self.__ebox.set_sensitive(value)


    def _setp_value(self, key, value):

        keycode, modifiers = value
        self.__button.set_label(self.__key2text(keycode, modifiers))
        
        self._set_config(value)
        self._setp(key, value)
