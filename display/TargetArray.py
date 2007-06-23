from ContainerTarget import ContainerTarget
from Layouter import Layouter, LayoutError
from utils.datatypes import *
from layout import Unit
import utils

import gtk


#
# Class for arrays of TargetDisplays.
#
class TargetArray(ContainerTarget):

    def __init__(self, name, parent):

        # the current layouter function
        self.__layouter = []

        # the class of the array elements
        self.__elementtype = None

        # the default settings of the array elements
        self.__elementsettings = None

        # children data of the array elements
        self.__elementchildren = []

        # the current elements of this array
        self.__children = []

        # mapping between unique IDs and targets
        self.__targets = {}

        ContainerTarget.__init__(self, name, parent)
        self.__layout = gtk.Fixed()
        self.__layout.show()

        self._register_property("length", TYPE_INT,
                                self._setp_length, self._getp_length)
        self._register_property("layout", TYPE_LIST,
                                self._setp_layout, self._getp)



    #
    # Returns the widget
    #
    def get_widget(self): return self.__layout



    #
    # Returns next child index
    #
    def get_next_child_index(self): return len(self.__children)



    def new_child(self, childtype, settings, children):

        self.__elementtype = childtype
        self.__elementsettings = settings
        self.__elementchildren = children

        # the array should be empty at the beginning but we need to create a
        # child so the array can connect to sensor output
        # remove eventually
        self.__add_child()
        self.__remove_child()



    def __on_observe_children(self, src, cmd):

        def f():
            x, y, w, h = src.get_geometry()
            self.__layout.move(src.get_widget(), x.as_px(), y.as_px())


        if (cmd == src.OBS_GEOMETRY and self.__children):
            utils.request_call(f)



    #
    # Adds an element to this array.
    #
    def __add_child(self):

        # use a unique ID
        settings = self.__elementsettings.copy()
        settings["id"] += "#" + str(len(self.__children))
        child = ContainerTarget.new_child(self, self.__elementtype,
                                          settings,
                                          self.__elementchildren)
        self.__children.append(child)

        x, y, w, h = child.get_geometry()
        self.__layout.put(child.get_widget(), x.as_px(), y.as_px())
        child.add_observer(self.__on_observe_children)

        if (not self._is_geometry_locked()): child.unlock_geometry()



    #
    # Removes an element from this array.
    #
    def __remove_child(self):
        assert(self.__children)

        child = self.__children.pop()
        self.__layout.remove(child.get_widget())
        child.remove_observer(self.__on_observe_children)

        self.get_layout_object().remove_child(child.get_layout_object())

        self._unregister_child(child)
        child.delete()



    #
    # Positions all elements of this array.
    #
    def __place_children(self):

        if (not self.__layouter): return
        parts = self.__layouter
        layout = parts[0]
        args = parts[1:]

        try:
            layouter = Layouter(layout)
        except LayoutError:
            return

        cnt = 0
        previous_id = ""
        for child in self.__children:
            x, y, w, h = child.get_geometry()
            rel, cx, cy = layouter.layout(cnt, args)
            cx = Unit.Unit(cx, Unit.UNIT_PX)
            cy = Unit.Unit(cy, Unit.UNIT_PX)

            cx, cy = child.get_anchored_coords(cx, cy, w, h)

            if (not rel):
                child.set_position(cx, cy)

            if (previous_id and rel):
                child.set_prop("relative-to", (previous_id, rel))

            previous_id = self.get_id_by_child(child)
            cnt += 1

        #utils.request_call(self.adjust_geometry)
        #self.adjust_geometry()



    # FIXME: remove eventually
    def distribute_sensor_output(self, sensor, indexes, key, value):

        index = int(indexes.pop(0))

        # add children, if necessary
        if (index >= len(self.__children)):
            while (index >= len(self.__children)): self.__add_child()
            self.__place_children()

        entries = self.__targets.get((sensor, index, key), [])
        for target, prop in entries:
            if (indexes):
                target.distribute_sensor_output(sensor, indexes[:],
                                                key, value)
            else:
                target.set_xml_prop(prop, value)



    #
    # "length" property.
    #
    def _setp_length(self, key, value):

        length = int(value)
        if (len(self.__children) != length):
            while (length > len(self.__children)): self.__add_child()
            while (length < len(self.__children)): self.__remove_child()
        self.__place_children()



    def _getp_length(self, key):

        return len(self.__children)



    #
    # "layout" property.
    #
    def _setp_layout(self, key, value):

        self.__layouter = value
        self.__place_children()
        self._setp(key, value)

