from ContainerTarget import ContainerTarget
from utils.datatypes import *
import utils

import gtk
import os

try:
    from utils.tiling import Tiling
except ImportError:
    import sys
    log("Could not import tiling module!")
    sys.exit(1)


#
# Class for grouping different targets together.
#
class TargetGroup(ContainerTarget):

    def __init__(self, name, parent):

        # flag for ensuring that only one collapse action takes place
        self.__block = 0

        # the maximum size values of all the children
        self.__max_size = (0, 0)

        ContainerTarget.__init__(self, name, parent)
        self.__layout = gtk.Fixed()
        self.__layout.show()

        self.__image = Tiling()
        self.__image.show()
        self.__layout.put(self.__image, 0, 0)

        self._register_property("bg-uri", TYPE_STRING,
                                self._setp_bg_uri, self._getp)
        self._register_property("bg-color", TYPE_STRING,
                                self._setp_bg_color, self._getp)

        self.add_observer(self.__on_observe_size)



    def delete(self):

        self.__image.destroy()
        self.__layout.destroy()
        del self.__image
        del self.__layout
        del self.__block
        del self.__max_size
        ContainerTarget.delete(self)



    def get_widget(self): return self.__layout


    def __on_observe_size(self, src, cmd):

        if (cmd == src.OBS_GEOMETRY):
            x, y, w, h = self.get_geometry()

            if (self._getp("bg-uri") or self._getp("bg-color")):
                ow, oh = self.__image.size_request()
                if ((w.as_px(), h.as_px()) != (ow, oh)):
                    self.__image.tile(w.as_px(), h.as_px())



    def new_child(self, childtype, settings, children):

        child = ContainerTarget.new_child(self, childtype, settings, children)
        if (not child.is_standalone()):
            x, y, w, h = child.get_geometry()
            self.__layout.put(child.get_widget(), x.as_px(), y.as_px())

        return child



    def child_observer(self, src, cmd):

        if (cmd == src.OBS_GEOMETRY):
            x, y, w, h = src.get_geometry()

            if (src.get_widget() in self.__layout.get_children()):
                self.__layout.move(src.get_widget(), x.as_px(), y.as_px())



    #
    # Sets the background color.
    #
    def __set_color(self, color):

        r, g, b, a = utils.parse_color(color)
        w, h = self.__layout.size_request()
        self.__image.set_from_color(r, g, b, a)
        self.__image.tile(w, h)



    #
    # Sets the background image.
    #
    def __set_background(self, uri):

        if (not uri):
            self.__set_color("#00000000")
            return

        from utils import vfs
        if (vfs.exists(uri)):
            try:
                data = vfs.read_entire_file(uri)
            except:
                return
            w, h = self.__layout.size_request()
            self.__image.set_from_data(data)
            self.__image.tile(w, h)



    #
    # "bg-uri" property.
    #
    def _setp_bg_uri(self, key, value):

        path = self._get_display().get_full_path(value)
        self.__set_background(path)
        self._setp(key, value)



    #
    # "bg-color" property.
    #
    def _setp_bg_color(self, key, value):

        self.__set_color(value)
        self._setp(key, value)

