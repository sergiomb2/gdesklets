from DisplayTarget import DisplayTarget
from layout import Unit
from utils.DOM import DOM
from utils.datatypes import *
from utils import dialog
from utils import vfs
import utils

import gtk

try:
    from utils import svg
except ImportError:
    import sys
    log("Could not import svg module!")
    sys.exit(1)


#
# Target where sensors can draw on.
#
class TargetCanvas(DisplayTarget):

    def __init__(self, name, parent):

        # a mini DOM for accessing the SVG data
        self.__dom = None

        # the previous size of the widget; used to detect resizings
        self.__old_size = (0, 0)

        # the size of the image
        self.__image_size = (100, 100)

        DisplayTarget.__init__(self, name, parent)

        self.__widget = gtk.Image()
        self.__widget.show()

        # the "graphics" property is not readable because otherwise it could
        # be used to spy out files on the user's system after loading them into
        # "uri"
        self._register_property("graphics", TYPE_STRING,
                                self._setp_graphics, None)
        self._register_property("dom", TYPE_OBJECT,
                                None, self._getp_dom)
        self._register_property("uri", TYPE_STRING,
                                self._setp_uri, self._getp)

        self._setp("graphics", "")

        # watch the element for geometry changes
        self.add_observer(self.__on_observe_size)



    def get_widget(self): return self.__widget



    def delete(self):

        del self.__dom
        del self.__widget
        DisplayTarget.delete(self)



    #
    # Observer for size.
    #
    def __on_observe_size(self, src, cmd, *args):

        x, y, w, h = src.get_geometry()
        if (cmd == src.OBS_GEOMETRY and
            (w.as_px(), h.as_px()) != self.__old_size):
            utils.request_call(self.__redraw)
            self.__old_size = (w.as_px(), h.as_px())



    #
    # Transforms the given coordinates into buffer space.
    #
    def __transform_coords(self, x, y):

        width, height = self.get_geometry()[2:4]
        tx = (width.as_px() / 2.0)  * (1.0 + float(x))
        ty = (height.as_px() / 2.0) * (1.0 - float(y))

        return (tx, ty)



    def __make_style(self, foreground, fill):

        s = "stroke:" + foreground
        if (fill): s+= ";fill:" + foreground
        else: s+= ";fill:none"
        out = "style='%s'" % s
        return out



    #
    # Performs the given drawing operations. This is used for backwards
    # compatibility. New code should directly send SVG data.
    #
    def __draw_svg(self, commands):

        w, h = self.get_geometry()[2:4]
        out = "<svg width='%d' height='%d'>" % (w.as_px(), h.as_px())
        current_fg = "rgb(0, 0, 0)"
        for c in commands:
            if (not c.strip()): continue
            parts = c.split()

            cmd, args = parts[0], parts[1:]

            if (cmd == "color"):
                color = args[0]
                gdkcolor = gtk.gdk.color_parse(color)
                current_fg = "rgb(%d, %d, %d)" \
                 % (gdkcolor.red >> 8, gdkcolor.green >> 8, gdkcolor.blue >> 8)

            elif (cmd == "line"):
                x1, y1, x2, y2 = args
                x1, y1 = self.__transform_coords(x1, y1)
                x2, y2 = self.__transform_coords(x2, y2)
                style = self.__make_style(current_fg, False)
                out += "<line x1='%f' y1='%f' x2='%f' y2='%f' %s/>" \
                       % (x1, y1, x2, y2, style)

            elif (cmd == "polygon"):
                fill = int(args[-1])
                style = self.__make_style(current_fg, fill)
                points = [ self.__transform_coords(args[i], args[i+1])
                           for i in range(0,len(args)-1, 2) ]
                if (points): path = "M%f %f " % (points.pop(0))
                while (points):
                    path += "L%f %f " % (points.pop(0))
                out += "<path d='%s' %s/>" % (path, style)

            elif (cmd == "rectangle"):
                x1, y1, x2, y2, fill = args
                style = self.__make_style(current_fg, fill)
                x1, y1 = self.__transform_coords(x1, y1)
                x2, y2 = self.__transform_coords(x2, y2)
                w = x2 - x1
                h = y2 - y1
                out += "<rect x='%f' y='%f' width='%f' height='%f' %s/>" \
                       % (x, y, w, h, style)

            #end if
        #end for
        out += "</svg>"
        self.__render(out)



    #
    # Renders the given SVG data.
    #
    def __render(self, data):

        def f():
            utils.request_call(self.__redraw)

        if (not data): return

        self.__dom = DOM(data).get_root()

        if (not self.__dom): return

        self.__dom.set_update_handler(f)

        # check if the SVG has dynamic or static size
        try:
            self.__image_size = \
              int(float(self.__dom["width"])), int(float(self.__dom["height"]))
        except KeyError:
            log("Error: width and/or height not given\n")
        except UserError:
            log("Error: Desklet contains errors. Please contact the author!\n No width and/or height given in the SVG root element (in a Canvas element).")
        except ValueError:
            try:
                self.__image_size = \
                            Unit.Unit(string = self.__dom["width"]).as_px(), \
                            Unit.Unit(string = self.__dom["height"]).as_px()
            except KeyError:
                pass

        self.__redraw()



    #
    # Redraws the canvas.
    #
    def __redraw(self):

        if (not self.__dom): return

        w, h = self.__widget.size_request()
        imgw, imgh = self.__image_size
        if (imgw == 0 or imgh == 0):
            log ("Warning: The desklet is broken. Image height or width is 0",
                 "Please contact the author to fix the problem.")
            return

        # crappy SVG needs the size to be given; just set it here so that it
        # dynamically takes the correct size
        self.__dom["width"] = str(w or 100)
        self.__dom["height"] = str(h or 100)

        # so that's why the XML parser inserted an empty <g> node... :)
        g = self.__dom.get_children()[0]
        g["transform"] = "scale(%f, %f)" % (float(w) / imgw,
                                            float(h) / imgh)

        svg.render(self.__widget, w, h, str(self.__dom))



    #
    # "graphics" property.
    #
    def _setp_graphics(self, key, value):

        # native SVG
        if (value and value.lstrip()[0] == "<"):
            self.__render(value)

        # legacy graphics language
        else:
            value = value.split(",")
            self.__draw_svg(value)

        self._setp(key, value)



    #
    # Returns the DOM object of the graphics.
    #
    def _getp_dom(self, key): return self.__dom



    #
    # Loads SVG from the given URI.
    #
    def _setp_uri(self, key, value):

        uri = self._get_display().get_full_path(value)
        try:
            data = vfs.read_entire_file(uri)
        except:
            log("Couldn't read file %s.\n" % uri)
            return

        self.__render(data)
        self._setp(key, value)

