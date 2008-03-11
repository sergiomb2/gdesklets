from TargetCanvas import TargetCanvas
from utils.datatypes import *


#
# Class for plotting graphs.
#
class TargetPlotter(TargetCanvas):

    def __init__(self, name, parent):

        # history of plot values
        self.__history = []

        # colors
        self.__bgcolor = ""
        self.__color = "navy"

        # scale range, initial value
        self.__minscale = 0
        self.__maxscale = 100

        TargetCanvas.__init__(self, name, parent)

        self._register_property("value", TYPE_FLOAT,
                                self._setp_value, self._getp)
        self._register_property("bg-color", TYPE_STRING,
                                self._setp_bgcolor, self._getp)
        self._register_property("color", TYPE_STRING,
                                self._setp_color, self._getp)
        self._register_property("size", TYPE_INT,
                                self._setp, self._getp)
        self._setp("size", 50)
        self._register_property("scala", TYPE_INT,
                                self._setp, self._getp)
        self._setp("scala", 0)
        self._register_property("scala-color", TYPE_STRING,
                                self._setp, self._getp)
        self._setp("scala-color", "black")
        self._register_property("scala-font", TYPE_STRING,
                                self._setp, self._getp)
        self._setp("scala-font", "Sans")

        # scale-bidir: not only scale the upper bound, but also the lower one
        self._register_property("scale-bidir", TYPE_BOOL,
                                self._setp, self._getp)
        self._setp("scale-bidir", False)
        # scale-holdmax: keep the maximum 'all-time' scaling, not only
        # max(history)
        self._register_property("scale-holdmax", TYPE_BOOL,
                                self._setp, self._getp)
        self._setp("scale-holdmax", False)

        self._register_property("bars", TYPE_BOOL,
                                self._setp, self._getp)
        self._setp("bars", False)


    #
    # Plots the values from the history.
    #
    def __plot(self):

        bg, fg = self.__bgcolor, self.__color
        min_value = self.__minscale
        max_value = self.__maxscale
        size = self.get_prop("size")

        x = 0.0
        delta_x = 100.0 / (size - 1)

        if (bg):
            try:
                color, opacity = self.__parse_color(bg)
            except ValueError, exc:
                log(`exc`)
                return

            body = "<rect x=\"0\" y=\"0\" width=\"100\" height=\"100\" " \
                   "style=\"stroke:%s;stroke-opacity:%d%%;fill:%s;" \
                   "fill-opacity:%d%%\"/>" % (color, opacity, color, opacity)
        else:
            body = ""

        if (self.__history):
            if ((self.get_prop("scale-holdmax")) == False):
                # reset scale range to default:
                max_value = 100
                min_value = 0
            max_value = max(max_value, max(self.__history))
            if (self.get_prop("scale-bidir")):
                min_value = min(min_value, min(self.__history))
            self.__minscale = min_value
            self.__maxscale = max_value
            scale = 100.0 / (max_value - min_value)

            history_size = min(len(self.__history), size)
            x, y = x, self.__history[-history_size]

            if (self.get_prop("bars")):
                body += "<path d=\"M%f %f " % (x, 100 + min_value * scale)
                for y in self.__history[-history_size + 1:]:
                    y = 100 - (y - min_value) * scale
                    body += "L%(x)f %(y)f " % vars()
                    x += delta_x
                    body += "M%f %f " % (x, 100 + min_value * scale)
            else:
                body += "<path d=\"M%f %f " % (x, 100 - (y - min_value) * scale)
                x += delta_x
                for y in self.__history[-history_size + 1:]:
                    y = 100 - (y - min_value) * scale
                    body += "L%(x)f %(y)f " % vars()
                    x += delta_x
            try:
                color, opacity = self.__parse_color(fg)
            except ValueError, exc:
                log(`exc`)
                return
            body += "\" style=\"stroke:%s;opacity:%d%%;fill:none\"/>" % \
                     (color, opacity)

        # draw scala
        scala = self.get_prop("scala")
        if (scala):
            scala_color = self.get_prop("scala-color")
            scala_font = self.get_prop("scala-font")
            for i in range(0, max_value + 1, scala):
                body += "<text x=\"0\" y=\"%d\" font-family=\"%s\" " \
                        "font-size=\"%d\" fill=\"%s\">%d</text>" \
                        % (max_value - i, scala_font, 5, scala_color, i)

        gfx = "<svg>" + body + "</svg>"
        self.set_prop("graphics", gfx)



    def __parse_color(self, value):

        if ("#" in value and len(value) == 9):
            opacity = float(int(value[7:], 16) / 255.0) * 100
            return (value[:7], opacity)
        elif (value.isalnum()):
            return (value, 100)
        else:
            raise ValueError("%s is an invalid color." % `value`)



    def _setp_value(self, key, value):

        self.__history.append(value)
        self.__plot()
        if (len(self.__history) > self.get_prop("size")):
            self.__history.pop(0)
        self._setp(key, value)



    def _setp_bgcolor(self, key, value):

        self.__bgcolor = value
        self.__plot()
        self._setp(key, value)


    def _setp_color(self, key, value):

        self.__color = value
        self.__plot()
        self._setp(key, value)

