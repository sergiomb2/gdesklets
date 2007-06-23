from sensor.Sensor import Sensor
from utils.datatypes import *
from utils import i18n
import time
import os


#
# FontSelector sensor by Psi (psiz _at_ free _dot_ fr)
# Adopted and modified by Martin Grimme.
#
class FontSelector(Sensor):

    def __init__(self, fontnumber="1", *fontargs):

        global _; _ = i18n.Translator("font-selector-sensor")


        # the number of fonts
        self.__fontnumber = int(fontnumber)

        # the font settings
        self.__fonts = []

        # the color settings
        self.__colors = []


        Sensor.__init__(self)
        self._watch_config(self.config_watcher)
        # setup configuration entries
        if (len(fontargs) == 1 and fontargs[0].find("  ") != -1):
            fontargs = \
               (fontargs[0].replace("   ", ",").replace("  ", ",")).split(",")
            print "Using spaces to separate font entries is deprecated."
            print "Use commas instead."

        fontargs = list(fontargs)
        for font_n in xrange(self.__fontnumber):
            if (fontargs): font = fontargs.pop(0)
            else: font = "Sans 8"
            if (fontargs): color = fontargs.pop(0)
            else: color = "black"
            self._set_config_type("font%i" % font_n, TYPE_STRING, font)
            self._set_config_type("color%i" % font_n, TYPE_STRING, color)
        #end for

        self._add_timer(500,self.__font_init)

    def config_watcher(self,key,value):
        data = self._new_output()
        data.set(key, value)
        self._send_output(data)

    #
    # Font init
    #
    def __font_init(self):

        fonts = []
        colors = []

        for font_n in xrange(self.__fontnumber):
            fonts.append(self._get_config("font%i" % font_n))
            colors.append(self._get_config("color%i" % font_n))


        if (fonts != self.__fonts or colors != self.__colors):
            self.__fonts = fonts
            self.__colors = colors

            data = self._new_output()
            for font_n in xrange(self.__fontnumber):
                data.set("font%i" % font_n, fonts[font_n])
                data.set("color%i" % font_n, colors[font_n])
            self._send_output(data)
        #end if

        return 0



    def get_configurator(self):

        configurator = self._new_configurator()
        configurator.set_name(_("Fonts"))
        configurator.add_title(_("Fonts settings"))

        for font_n in xrange(self.__fontnumber):
            configurator.add_font_selector(_("Font #%i:" % font_n),
                                           "font%i" % font_n,
                               _("Font #%i used in the labels" % font_n))
            configurator.add_color_selector(_("Font color #%i:" % font_n),
                                            "color%i" % font_n,
                               _("Font color #%i used in the labels" % font_n))
        #end for

        return configurator



def new_sensor(args): return FontSelector(*args)
