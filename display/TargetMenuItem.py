from ContainerTarget import ContainerTarget
from utils.datatypes import *
from utils.Struct import Struct

import gtk


#
# Class for menu items.
#
class TargetMenuItem(ContainerTarget):

    __ACTION_ACTIVATE = "activate"
    __DEFAULT_SLOT = "default slot"


    def __init__(self, name, parent):

        self.__menuitem = None

        ContainerTarget.__init__(self, name, parent)

        self._register_property("label", TYPE_STRING,
                                self._setp_label, self._getp)
        self._register_property("slot", TYPE_STRING,
                                self._setp_slot, self._getp)
        self._register_property("active", TYPE_BOOL,
                                self._setp_active, self._getp)
        self.set_prop("slot", self.__DEFAULT_SLOT)
        self.set_prop("label", "")
        self.set_prop("active", True)

        self._register_action(self.__ACTION_ACTIVATE)


    def get_widget(self): return self.__menuitem
    def is_standalone(self): return True


    def __on_activate(self, src):

        self._get_display().send_action(self, self.__ACTION_ACTIVATE,
                                        Struct(_args = []))


    def _setp_label(self, key, value):

        if (self.__menuitem):
            submenu = self.__menuitem.get_submenu()
            self.__menuitem.remove_submenu()
            self.__menuitem.destroy()
        else:
            submenu = None

        if (value):
            # create menu item
            self.__menuitem = gtk.MenuItem(value)
        else:
            # create separator
            self.__menuitem = gtk.MenuItem()

        self.__menuitem.show()
        self.__menuitem.connect("activate", self.__on_activate)
        if (submenu): self.__menuitem.set_submenu(submenu)
        self._setp(key, value)


    def _setp_slot(self, key, value):

        self._setp(key, value)


    def _setp_active(self, key, value):

        self._setp(key, value)


    def set_handler(self, handler, *args):

        def f(src, handler, args):
            handler(*args)

        self.__menuitem.connect("activate", f, handler, args)



    def prepare(self):

        child = self._get_child()
        if (child): child.prepare()
        active = self.get_prop("active")
        self.__menuitem.set_sensitive(active)


    def new_child(self, childtype, settings, children):

        child = ContainerTarget.new_child(self, childtype, settings, children)
        self.__menuitem.set_submenu(child.get_widget())

        return child
