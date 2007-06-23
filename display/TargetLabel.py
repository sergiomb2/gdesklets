from DisplayTarget import DisplayTarget
from utils.datatypes import *
from layout import Unit
import utils

import gobject
import gtk
import pango
import re

try:
    from utils.tiling import Tiling
except ImportError:
    import sys
    log("Could not import tiling module!")
    sys.exit(1)

# determine the locale
import commands

fail, CHARMAP = commands.getstatusoutput("locale charmap")

if (fail or not CHARMAP):
    log("Could not detect character encoding.")
    CHARMAP = "ASCII"


class TargetLabel(DisplayTarget):

    # regular expression for parsing font description strings
    __RE_FONT = re.compile("(?P<name>.+?)"
                           "(?P<size>[0-9\.]+)"
                           "(?P<unit>[a-z%]+)?$")


    def utf8_to_utf8(value):

        if (isinstance(value, unicode)):
            try:
                value = value.encode("UTF-8", "replace")
            except ValueError:
                log("Unicode -> UTF-8 convertion failed !!!")
                raise

        elif (not isinstance(value, str)):
            # int, float, long, list, tuple, instance
            value = str(value)

        return value


    def charmap_to_utf8(value):

        if (isinstance(value, str)):
            try:
                value = unicode(value, CHARMAP, "ignore")
            except LookupError:
                # may be it's already UTF-8 ?
                value = unicode(value, "UTF-8", "replace")

        if (isinstance(value, unicode)):
            try:
                value = value.encode("UTF-8", "replace")
            except ValueError:
                log("Unicode -> UTF-8 convertion failed !!!")
                raise

        else:
            # int, float, long, list, tuple, instance
            value = str(value)

        return value


    #
    # Converts the given string to UTF-8 format.
    #
    if (CHARMAP == 'UTF-8'):
        __utf8ify = staticmethod(utf8_to_utf8)
    else:
        __utf8ify = staticmethod(charmap_to_utf8)



    def __init__(self, name, parent):

        self.__old_value = ""
        self.__font_description = None
        self.__wrap_at = -1

        self.__size = (0, 0)

        DisplayTarget.__init__(self, name, parent)

        self.__widget = Tiling()
        self.__pango_context = self.__widget.get_pango_context()
        self.__pango_context.set_base_dir(pango.DIRECTION_LTR)
        self.__pango_layout = pango.Layout(self.__pango_context)
        self.__color = (0, 0, 0, 255)
        self.__font_description = self.__pango_context.get_font_description()
        self.__widget.show()

        # i guess a label has to accept everything printable for its value
        # these days
        self._register_property("value", TYPE_ANY,
                                self._setp_value, self._getp)
        self._register_property("color", TYPE_STRING,
                                self._setp_color, self._getp)
        self._register_property("font", TYPE_STRING,
                                self._setp_font, self._getp)
        self._register_property("wrap-at", TYPE_UNIT,
                                self._setp_wrap_at, self._getp)

        self._setp("value", "")
        self._setp("color", "black")
        self.set_prop("font", "Sans 8")
        self.set_prop("wrap-at", Unit.Unit(0, Unit.UNIT_PX))

        # watch the widget for geometry changes; we need this for percentual
        # font sizes
        self.add_observer(self.__on_observe_size)


    def get_widget(self): return self.__widget


    def __on_observe_size(self, src, cmd, *args):

        x, y, w, h = src.get_geometry()
        if (cmd == src.OBS_GEOMETRY):
            self.__size = (w.as_px(), h.as_px())
            self.__set_wrap(self.get_prop("wrap-at"))
            self.__set_font(self.get_prop("font"))
            self.__set_value(self.get_prop("value"))


    #
    # Renders the given text.
    #
    def __render_text(self, layout):

        width, height = layout.get_pixel_size()

        # render font
        pmap = gtk.gdk.Pixmap(gtk.gdk.get_default_root_window(),
                              width, height * 2)
        gc = pmap.new_gc()
        gc.set_foreground(self.__widget.get_colormap().alloc_color("black"))
        pmap.draw_rectangle(gc, True, 0, 0, width, height)
        gc.set_foreground(self.__widget.get_colormap().alloc_color("white"))
        pmap.draw_rectangle(gc, True, 0, height, width, height)

        r, g, b, a = self.__color
        col = "#" + ("0" + hex(r)[2:])[-2:] + \
                    ("0" + hex(g)[2:])[-2:] + \
                    ("0" + hex(b)[2:])[-2:]
        gc.set_foreground(
            gtk.gdk.get_default_root_window().get_colormap().alloc_color(col))
        pmap.draw_layout(gc, 0, 0, layout)
        pmap.draw_layout(gc, 0, height, layout)

        #  then copy to image
        self.__widget.set_from_drawable(pmap, True)
        width, height = self.__size
        if (width and height):
            self.__widget.render(width, height, a / 255.0, 1)


    def __make_label(self):

        value = self.__old_value

        self.__pango_layout.set_markup(value)
        self.__pango_layout.set_font_description(self.__font_description)
        self.__pango_layout.set_width(self.__wrap_at * pango.SCALE)
        width, height = self.__pango_layout.get_pixel_size()

        if (width and height):
            self.__render_text(self.__pango_layout)
            self.__widget.show()
        else:
            self.__widget.hide()

        self.set_size(Unit.Unit(width, Unit.UNIT_PX),
                      Unit.Unit(height, Unit.UNIT_PX))



    def __set_value(self, value):

        value = self.__utf8ify(value)
        self.__old_value = value
        self.__make_label()



    def __set_font(self, font):

        m = TargetLabel.__RE_FONT.match(font)
        if (m):
            name = m.group("name")
            unit = m.group("unit") or Unit.UNIT_PT  # pt is default for fonts
            size = m.group("size")
            if (size):
                size = float(size)
                if (unit == Unit.UNIT_PERCENT):
                    height = self._get_parent().get_geometry()[3]
                    # don't allow 0 pixels height
                    size = max(1, height.as_pt() * (size / 100.0))
                    unit = Unit.UNIT_PT
                u = Unit.Unit(size, unit)
                size = u.as_pt()
                font = "%s %f" % (name, size)

        self.__font_description = pango.FontDescription(font)
        self.__pango_context.set_font_description(self.__font_description)
        #self.__widget.set_size_request(-1, -1)


    def __set_color(self, color):

        self.__color = utils.parse_color(color)


    def __set_wrap(self, value):

        width = self._get_parent().get_geometry()[2]
        if (width > Unit.ZERO): value.set_100_percent(width.as_px())
        size = value.as_px()

        if (size == 0):
            self.__wrap_at = -1
        else:
            self.__wrap_at = size


    #
    # "value" property.
    #
    def _setp_value(self, key, value):

        if (value != self.__old_value):
            self.__set_value(value)
            self._setp(key, value)


    #
    # "font" property.
    #
    def _setp_font(self, key, value):

        if (value != self.get_prop("font")):
            self.__set_font(value)
            self._setp(key, value)
            self.__make_label()
            #self.__set_value(self.get_prop("value"))


    #
    # "color" property.
    #
    def _setp_color(self, key, value):

        self.__set_color(value)
        self._setp(key, value)
        self.__make_label()


    #
    # "wrap-at" property.
    #
    def _setp_wrap_at(self, key, value):

        self.__set_wrap(value)
        self._setp(key, value)
        self.__make_label()
