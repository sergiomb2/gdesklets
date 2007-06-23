from TargetGroup import TargetGroup
from utils.datatypes import *
from layout import Unit


class TargetDisplay(TargetGroup):

    def __init__(self, name, parent):

        TargetGroup.__init__(self, name, parent)

        self._register_property("desktop-borders", TYPE_UNIT_LIST,
                                self._setp_container_stuff, self._getp)

        self._register_property("window-flags", TYPE_LIST,
                                self._setp_container_stuff, self._getp)
        self._register_property("shape", TYPE_STRING,
                                self._setp_container_stuff, self._getp)
        self._register_property("icon", TYPE_STRING,
                                self._setp_container_stuff, self._getp)
        self._register_property("title", TYPE_STRING,
                                self._setp_container_stuff, self._getp)

        self._register_property("path", TYPE_STRING, None, self._getp)
        self._setp("path", self._get_display().get_path())

        self.set_prop("x", Unit.Unit())
        self.set_prop("y", Unit.Unit())


        self._setp_container_stuff("window-flags", ["decorated"])



    #
    # Container properties.
    #
    def _setp_container_stuff(self, key, value):

        self._get_display().set_prop(key, value)
        self._setp(key, value)
