from ContainerTarget import ContainerTarget
from utils.datatypes import *

import gtk


#
# Class for menus.
#
class TargetMenu(ContainerTarget):

    def __init__(self, name, parent):

        # the list of available slots; a slot is where items can be put in
        self.__slots = []

        ContainerTarget.__init__(self, name, parent)
        self.__menu = gtk.Menu()

        self._register_property("popup", TYPE_INT,
                                None, self._getp)
        self._setp("popup", self.__popup)



    def get_widget(self): return self.__menu
    def is_standalone(self): return True



    #
    # Returns the list of available slots.
    #
    def get_slots(self):

        slots = []
        for slotname, contents in self.__slots:
            slots.append(slotname)

        return slots



    #
    # Inserts a new slot at the given position.
    #
    def insert_slot(self, name, position):

        slot = (name, [])
        self.__slots.insert(position, slot)



    #
    # Removes the given slot.
    #
    def remove_slot(self, name):

        for slotname, contents in self.__slots:
            if (slotname == name):
                self.__slots.remove((slotname, contents))
                break



    #
    # Adds an item to the given slot.
    #
    def add_to_slot(self, name, item):

        for slotname, contents in self.__slots:
            if (slotname == name):
                contents.append(item)
                break



    #
    # Removes the given item from the given slot.
    #
    def remove_from_slot(self, name, item):

        for slotname, contents in self.__slots:
            if (slotname == name):
                contents.remove(item)
                break



    #
    # Prepares the menu for displaying.
    #
    def prepare(self):

        # clear menu
        for c in self.__menu.get_children(): self.__menu.remove(c)

        # fill menu
        for name, contents in self.__slots:
            for item in contents:
                self.__menu.append(item.get_widget())
                item.prepare()



    def __popup(self):

        self._get_display().queue_menu(self)



    def new_child(self, childtype, settings, children):

        child = ContainerTarget.new_child(self, childtype, settings, children)
        slot = child.get_prop("slot")
        if (not slot in self.get_slots()):
            self.insert_slot(slot, len(self.get_slots()))
        self.add_to_slot(slot, child)

        return child
