from ContainerTarget import ContainerTarget
from utils.datatypes import *
from layout import Unit
from utils import vfs
import utils

import os
import gtk

try:
    from utils.tiling import Tiling
except ImportError:
    import sys
    log("Could not import tiling module!")
    sys.exit(1)


#
# Class for putting frames around targets.
#
class TargetFrame(ContainerTarget):

    def __init__(self, name, parent):

        self.__frame_widths = [Unit.ZERO] * 4
        self.__images = []


        ContainerTarget.__init__(self, name, parent)
        self.__table = gtk.Table(3, 3)
        self.__table.set_direction(gtk.TEXT_DIR_LTR)
        self.__table.show()

        r, g, b, a = utils.parse_color("black")
        for x, y in [(0, 1), (1, 0), (2, 1), (1, 2),
                     (0, 0), (2, 0), (2, 2), (0, 2)]:
            img = Tiling()
            img.set_from_color(r, g, b, a)
            img.show()
            self.__table.attach(img, x, x + 1, y, y + 1)
            self.__images.append(img)

        self.__box = gtk.HBox()
        self.__box.show()
        self.__table.attach(self.__box, 1, 2, 1, 2)

        self._register_property("border-uris", TYPE_LIST,
                                self._setp_border_uris, self._getp)
        self._register_property("border-width", TYPE_UNIT_LIST,
                                self._setp_border_width, self._getp)
        self._register_property("color", TYPE_STRING,
                                self._setp_border_color, self._getp)

        self.set_prop("border-width",
                      [Unit.Unit(2, Unit.UNIT_PX), Unit.Unit(2, Unit.UNIT_PX),
                       Unit.Unit(2, Unit.UNIT_PX), Unit.Unit(2, Unit.UNIT_PX)])
        self._setp("color", "black")


        # watch for geometry changes
        self.add_observer(self.__on_observe_size)



    def get_widget(self): return self.__table

    def new_child(self, childtype, settings, children):

        child = ContainerTarget.new_child(self, childtype, settings, children)
        self.__box.add(child.get_widget())
        self.__redraw_frame()



    #
    # Observer for size changes.
    #
    def __on_observe_size(self, src, cmd, *args):

        x, y, w, h = src.get_geometry()
        if (cmd == src.OBS_GEOMETRY and
                                (w.as_px() != 0) and (h.as_px() != 0)):
            self.__redraw_frame()



    def __redraw_frame(self, src = None, event = None):

        x, y, w, h = self.get_geometry()
        w1, h1, w2, h2 = self.__frame_widths

        iw = max(Unit.ZERO, w - w1 - w2)
        ih = max(Unit.ZERO, h - h1 - h2)

        self.__box.set_size_request(iw.as_px(), ih.as_px())
        cnt = 0
        for bw, bh in ((w1, ih), (iw, h1),
                       (w2, ih), (iw, h2),
                       (w1, h1), (w2, h1),
                       (w2, h2), (w1, h2)):
            img = self.__images[cnt]
            cnt += 1

            if (bw.as_px() == 0 or bh.as_px() == 0):
                img.hide()
            else:
                img.show()

                img.tile(bw.as_px(), bh.as_px())
                img.set_size_request(bw.as_px(), bh.as_px())
        #end for



    def __set_border_width(self, args):

        for i in xrange(len(args)):
            self.__frame_widths[i] = args[i]

        self.get_layout_object().set_border_width(*args)



    def __set_border(self, args):

        cnt = 0
        for uri in args:
            uri = self._get_display().get_full_path(uri)
            if (vfs.exists(uri)):
                try:
                    data = vfs.read_entire_file(uri)
                except:
                    return
                self.__images[cnt].set_from_data(data)
            cnt += 1

        self.__redraw_frame()



    def __set_border_color(self, color):

        r, b, g, a = utils.parse_color(color)
        for cnt in range(8):
            self.__images[cnt].set_from_color(r, g, b, a)

        self.__redraw_frame()



    def get_border_size(self):

        w1, h1, w2, h2 = self.__frame_widths
        return (w1, h1, w2, h2)



    def _setp_border_uris(self, key, value):

        self.__set_border(value)
        self._setp(key, value)



    def _setp_border_color(self, key, value):

        self.__set_border_color(value)
        self._setp(key, value)



    def _setp_border_width(self, key, value):

        self.__set_border_width(value)
        self._setp(key, value)
