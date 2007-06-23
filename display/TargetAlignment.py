from ContainerTarget import ContainerTarget
from DisplayTarget import DisplayTarget
from utils.datatypes import *
from layout import Unit

import gtk


#
# Class for aligning targets.
#
class TargetAlignment(ContainerTarget):

    def __init__(self, name, parent):

        self.__alignment = (0.0, 0.0)

        ContainerTarget.__init__(self, name, parent)
        self.__align = gtk.Alignment(0.5, 1, 0, 0)
        self.__align.set_direction(gtk.TEXT_DIR_LTR)
        self.__align.show()

        self._register_property("align-x", TYPE_FLOAT,
                                self._setp_alignment, self._getp)
        self._register_property("align-y", TYPE_FLOAT,
                                self._setp_alignment, self._getp)


    def get_widget(self): return self.__align


    def new_child(self, childtype, settings, children):

        child = ContainerTarget.new_child(self, childtype, settings, children)
        self.__align.add(child.get_widget())



    #
    # Alignment properties.
    #
    def _setp_alignment(self, key, value):

        if (key == "align-x"):
            ax, ay = self.__alignment
            self.__align.set(value, ay, 0, 0)
            self.__alignment = (value, ay)

        elif (key == "align-y"):
            ax, ay = self.__alignment
            self.__align.set(ax, value, 0, 0)
            self.__alignment = (ax, value)

        child = self._get_child()
        nil, nil, aw, ah = self.get_geometry()
        nil, nil, cw, ch = child.get_geometry()
        hvalue, vvalue = self.__alignment
        x = (aw - cw) * hvalue
        y = (ah - ch) * vvalue
        child.set_prop("x", x)
        child.set_prop("y", y)
        
        self._setp(key, value)
