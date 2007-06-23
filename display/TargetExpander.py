from ContainerTarget import ContainerTarget
from utils.datatypes import *
from utils.Struct import Struct
from layout import Unit
from utils import vfs

import gtk
import os


_STATE_VISIBLE = 0
_STATE_HIDDEN = 1


#
# Class for target expander.
#
class TargetExpander(ContainerTarget):

    __ACTION_EXPAND = "expand"

    def __init__(self, name, parent):

        self.__show_state = _STATE_VISIBLE

        ContainerTarget.__init__(self, name, parent)
        self.__widget = gtk.Table(2, 2)
        self.__widget.show()

        self.__icon = gtk.Image()
        self.__icon.show()
        self.__widget.attach(self.__icon, 0, 1, 0, 1, 0, 0, 0, 0)

        dummy = gtk.HBox(); dummy.show()
        self.__widget.attach(dummy, 0, 1, 1, 2,
                             gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
                             0, 0)

        self._register_property("expanded", TYPE_BOOL,
                                 self._setp_expanded, self._getp)
        self._register_property("icon-uri", TYPE_STRING,
                                 self._setp_icon, self._getp)
        self._register_action(self.__ACTION_EXPAND)


    def get_widget(self): return self.__widget


    def __on_click(self, src, event):

        if (self.__show_state == _STATE_VISIBLE):
            self.__set_expanded(False)
        else:
            self.__set_expanded(True)


    def __set_expanded(self, value):

        if (value): self.__show_state = _STATE_VISIBLE
        else: self.__show_state = _STATE_HIDDEN

        iconw, iconh = self.__icon.size_request()

        if (self.__show_state == _STATE_VISIBLE):
            self._get_child().set_prop("visible", True)
            width, height = self._get_child().get_geometry()[2:]
            self.set_size(iconw + width.as_px(), height.as_px())
            expand = True
        else:
            self._get_child().set_prop("visible", False)
            self.set_size(iconw, iconh)
            expand = False

        self._get_display().send_action(self, self.__ACTION_EXPAND,
                                        Struct(expand = expand,
                                               _args = [expand]))


    def __set_icon(self, uri):

        if (not uri): return
        uri = self._get_display().get_full_path(uri)
        loader = gtk.gdk.PixbufLoader()
        try:
            data = vfs.read_entire_file(uri)
        except:
            return
        try:
            loader.write(data, len(data))
        except:
            log("Invalid image format.")
            return

        loader.close()
        pbuf = loader.get_pixbuf()
        self.__icon.set_from_pixbuf(pbuf)



    def get_border_size(self):

        w, h = self.__icon.size_request()
        if (self.__show_state == _STATE_VISIBLE):
            return (Unit.Unit(w, Unit.UNIT_PX), Unit.ZERO,
                    Unit.ZERO, Unit.ZERO)
        else:
            return (Unit.Unit(w, Unit.UNIT_PX), Unit.Unit(h, Unit.UNIT_PX),
                    Unit.ZERO, Unit.ZERO)


    def _setp_expanded(self, key, value):

        self.__set_expanded(value)
        self._setp(key, value)


    def _setp_icon(self, key, value):

        self.__set_icon(value)
        self._setp(key, value)


    def get_container_geometry(self):

        if (self._get_child()):
            x, y, w, h = self._get_child().get_geometry()
            iconw, iconh = self.__icon.size_request()
        else:
            x, y, w, h = self.get_geometry()

        return (x, y, w, h)


    def handle_action(self, action, px, py, args):

        ContainerTarget.handle_action(self, action, px, py, args)

        w, h = self.__icon.size_request()
        if (0 <= px.as_px() <= w and 0 <= py.as_px() <= h):
            if (action == self.ACTION_CLICK):
                if (self.__show_state == _STATE_VISIBLE):
                    self.__set_expanded(False)
                else:
                    self.__set_expanded(True)


    def new_child(self, childtype, settings, children):

        child = ContainerTarget.new_child(self, childtype, settings, children)
        self.__widget.attach(child.get_widget(), 1, 2, 0, 2,
                             gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
                             0, 0)
