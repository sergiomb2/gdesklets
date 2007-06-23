from DisplayTarget import DisplayTarget
from utils.datatypes import *
from layout import Unit
from utils import vfs
import utils

import gtk

try:
    from utils.tiling import Tiling
except ImportError:
    import sys
    log("Could not import tiling module!")
    sys.exit(1)


#
# Class for image targets.
#
class TargetImage(DisplayTarget):

    def __init__(self, name, parent):

        self.__size = (0, 0)

        # the original image size
        self.__original_size = (0, 0)

        # the current saturation value
        self.__current_saturation = 0.0

        # the current opacity value
        self.__current_opacity = 0.0

        DisplayTarget.__init__(self, name, parent)

        self.__widget = Tiling()
        self.__widget.show()

        self._register_property("uri", TYPE_STRING,
                                self._setp_uri, self._getp)
        self._register_property("saturation", TYPE_FLOAT,
                                self._setp_saturation, self._getp)
        self._register_property("scale", TYPE_FLOAT,
                                self._setp_scale, self._getp)
        self._register_property("opacity", TYPE_FLOAT,
                                self._setp_opacity, self._getp)
        self._register_property("image-width", TYPE_UNIT,
                                self._setp_image_size, self._getp_image_size)
        self._register_property("image-height", TYPE_UNIT,
                                self._setp_image_size, self._getp_image_size)

        self._setp("image-width", Unit.Unit())#-1, Unit.UNIT_PX))
        self._setp("image-height", Unit.Unit())#-1, Unit.UNIT_PX))
        self._setp("opacity", 1.0)
        self._setp("saturation", 1.0)
        self._setp("scale", 1.0)

        # watch the parent for geometry changes
        self.add_observer(self.__on_observe_size)



    def get_widget(self):

        return self.__widget



    def delete(self):

        DisplayTarget.delete(self)



    #
    # Observer for size.
    #
    def __on_observe_size(self, src, cmd, *args):

        x, y, w, h = src.get_geometry()
        if (cmd == src.OBS_GEOMETRY and
            (w.as_px(), h.as_px()) != self.__size):
            self.__compute_size()
            utils.request_call(self.__render_image)
            self.__size = (w.as_px(), h.as_px())



    #
    # Loads the image from the given URI.
    #
    def __load_image(self, uri):

        if (not uri): return

        try:
            data = vfs.read_entire_file(uri)
        except:
            return

        try:
            self.__widget.set_from_data(data)
            self.__original_size = self.__widget.get_size()

        except ValueError, exc:
            log(`exc`)
            return



    #
    # Computes the image size.
    #
    def __compute_size(self):

        # get image-width, image-height
        imgwidth = self._getp("width")
        imgheight = self._getp("height")
        origwidth, origheight = self.__original_size
        width = imgwidth.as_px()
        height = imgheight.as_px()

        # scale aspect-ratio
        if (imgwidth.is_unset() and imgheight.is_unset()):
            width = origwidth
            height = origheight
        elif (imgwidth.is_unset() and origheight > 0):
            width = height * (origwidth / float(origheight))
        elif (imgheight.is_unset() and origwidth > 0):
            height = (width * origheight) / float(origwidth)

        # apply scale
        scale = self.get_prop("scale")
        # some authors don't pay attention, let's catch it
        if (scale <= 0.0): scale = 1.0
        width = int(width * scale)
        height = int(height * scale)

        # set size
        self.set_size(Unit.Unit(width, Unit.UNIT_PX),
                      Unit.Unit(height, Unit.UNIT_PX))
        utils.request_call(self.__render_image)



    #
    # Renders the image.
    #
    def __render_image(self):

        if (0 in self.__original_size): return

        w, h, = self.get_geometry()[2:]
        imgwidth = w.as_px()
        imgheight = h.as_px()

        if (imgwidth == 0 or imgheight == 0): return

        saturation = self.get_prop("saturation")
        opacity = self.get_prop("opacity")

        # if nothing has changed, do nothing
        #if ((imgwidth, imgheight, saturation, opacity) ==
        #    (self.__current_width, self.__current_height,
        #     self.__current_saturation, self.__current_opacity)):
        #    return

        self.__widget.render(imgwidth, imgheight, opacity, saturation)
        self.__current_width = imgwidth
        self.__current_height = imgheight
        self.__current_opacity = opacity
        self.__current_saturation = saturation



    #
    # "uri" property.
    #
    def _setp_uri(self, key, value):

        path = self._get_display().get_full_path(value)
        try:
            self.__load_image(path)

        except:
            log("Failed to set URI %s for key %s." % (path, key))
            return

        self.__compute_size()
        self._setp(key, value)



    #
    # "opacity" property.
    #
    def _setp_opacity(self, key, value):

        value = min(1.0, max(0.0, value))
        old_opac = self.get_prop("opacity")
        if (abs(value - old_opac) > 0.01):
            self._setp(key, value)
            utils.request_call(self.__render_image)



    #
    # "saturation" property.
    #
    def _setp_saturation(self, key, value):

        old_sat = self.get_prop("saturation")
        if (abs(value - old_sat) > 0.01 ):
            self._setp(key, value)
            utils.request_call(self.__render_image)



    #
    # "scale" property.
    #
    def _setp_scale(self, key, value):

        old_scale = self.get_prop("scale")
        if (abs(value - old_scale) > 0.01):
            self._setp(key, value)
            self.__compute_size()



    #
    # "image-width" and "image-height" properties.
    #
    def _setp_image_size(self, key, value):
        assert (isinstance(value, Unit.Unit))

        if (key == "image-width" and
              value != self._getp("image-width")):
            self.set_prop("width", value)
            self._setp(key, value)

        elif (key == "image-height" and
              value != self._getp("image-height")):
            self.set_prop("height", value)
            self._setp(key, value)

        self.__compute_size()


    #
    # "image-height" property.
    #
    def _getp_image_size(self, key):

        if (key == "image-width"):
            return self._getp(key)
        elif (key == "image-height"):
            return self._getp(key)

