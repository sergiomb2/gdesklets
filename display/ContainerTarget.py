from layout import Unit
from utils import dialog
from utils.datatypes import *
from DisplayTarget import DisplayTarget

import utils

import gobject
import gtk


#
# Abstract class for targets that can contain others.
#
class ContainerTarget(DisplayTarget):

    __slots__ = ('__children', '__children_id', '__ids', '__relatives')

    def __init__(self, name, parent):

        # the list is necessary for preserving order
        self.__children = []

        # mapping: id -> child
        self.__children_id = {}

        # mapping: child -> id
        self.__ids = {}

        # the relative-relations: id_of_relative -> [child]
        self.__relatives = {}

        DisplayTarget.__init__(self, name, parent)



    #
    # Observer callback for watching children.
    #
    def child_observer(self, src, cmd): pass



    #
    # Creates a new child of the given type.
    #
    def new_child(self, childtype, settings, children):

        import targetregistry
        cid = settings["id"]

        child = targetregistry.create(childtype, self)
        only_one = targetregistry.one_child(self.get_name())

        if (only_one and len(self.__children) > 0):
            log("Warning: The %s container accepts only one child."
                % self.get_name(),
                is_warning = True)
        self._register_child(child, cid)
        child.get_widget().show()

        for t, s, c in children:
            child.new_child(t, s, c)

        for key, value in settings.items():
            child.set_xml_prop(key, value)

        return child



    def _register_child(self, child, cid):

        self.__children_id[cid] = child
        self.__ids[child] = cid
        self.__children.append(child)
        self._get_display().add_target_to_script(cid, child)



    def _unregister_child(self, child):

        cid = self.__ids[child]

        try:
            del self.__children_id[cid]
        except KeyError:
            pass

        try:
            del self.__ids[child]
        except KeyError:
            pass

        self.__children.remove(child)



    def _get_children(self): return self.__children[:]



    def _get_child(self):

        if (not self.__children): return
        else: return self.__children[0]



    def get_child_by_id(self, ident): return self.__children_id.get(ident)
    def get_id_by_child(self, child): return self.__ids.get(child)



    def delete(self):

        for c in self._get_children():
            c.delete()
            self._unregister_child(c)
            del c
        self.__children = []
        self.__children_id.clear()
        self.__ids.clear()

        del self.__children
        del self.__children_id
        del self.__ids
        del self.__relatives
        DisplayTarget.delete(self)



    #
    # Override this method if the container size differs from the target size.
    #
    def get_container_geometry(self):

        return self.get_geometry()



    #
    # Returns the border size of this container. Override this method to return
    # the sizes of the four borders (left, top, right, bottom).
    #
    def get_border_size(self):

        return (Unit.ZERO, Unit.ZERO, Unit.ZERO, Unit.ZERO)



    #
    # Containers which set index values for the children override this method.
    #
    def get_next_child_index(self): return -1



    def detect_leave(self, stamp):

        if (not self._is_active()): return
        DisplayTarget.detect_leave(self, stamp)
        for c in self.__children:
            c.detect_leave(stamp)



    def unlock_geometry(self):

        self._geometry_lock = False
        for c in self._get_children(): c.unlock_geometry()

