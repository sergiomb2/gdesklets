import gtk

from TargetGroup import TargetGroup
from utils.datatypes import *
from layout import Unit


#
# The gauge is a decorator that can turn anything into a gauge.
#
class TargetGauge(TargetGroup):

    __HORIZONTAL = "horizontal"
    __VERTICAL = "vertical"


    def __init__(self, name, parent):

        TargetGroup.__init__(self, name, parent)

        self._register_property("fill", TYPE_FLOAT,
                                self._setp_fill, self._getp)
        self._register_property("orientation", TYPE_STRING,
                                self._setp_orientation, self._getp)
        self._setp("fill", 100)
        self._setp("orientation", self.__HORIZONTAL)


    def new_child(self, childtype, settings, children):

        child = TargetGroup.new_child(self, childtype, settings, children)
        child.add_observer(self.__on_observe_child)


    def __on_observe_child(self, src, cmd, *data):

        if (cmd == src.OBS_GEOMETRY):
            self.set_prop("fill", self.get_prop("fill"))


    #
    # "fill" property.
    #
    def _setp_fill(self, key, value):

        value = max(0, min(value, 100))
        x, y, width, height = self._get_child().get_geometry()
        width = width.as_pt()
        height = height.as_pt()
        orientation = self.get_prop("orientation")
        if (orientation == self.__HORIZONTAL):
            width = int(width * (value / 100.0))
            self.set_prop("width", Unit.Unit(width, Unit.UNIT_PT))
        else:
            height = int(height * (value / 100.0))
            self.set_prop("height", Unit.Unit(height, Unit.UNIT_PT))

        self._setp(key, value)


    #
    # "orientation" property.
    #
    def _setp_orientation(self, key, value):

        self.set_prop("fill", self.get_prop("fill"))
        self._setp(key, value)
