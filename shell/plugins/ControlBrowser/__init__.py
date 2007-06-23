from shell.Plugin import Plugin
from shell.ItemBrowser import ItemBrowser
from plugin.Interface import Interface
from ControlInspector import ControlInspector
from main import HOME

import gtk
import gobject
import os
import textwrap
import string



class UI_ControlBrowser(Plugin):

    def init(self):

        self.__collection = self._get_plugin("Core_ControlCollection")
        self.__browser = ItemBrowser(self.__search_handler,
                                     self.__item_renderer,
                                     gtk.gdk.Pixbuf, gobject.TYPE_STRING,
                                     gobject.TYPE_STRING)
        self.__browser.add_observer(self.__on_activate)

        for name, items in \
           [(_("by interface"), self.__get_interfaces(self.__collection)),
          (_("alphabetically"), self.__get_alphabetically(self.__collection))]:
            self.__browser.add_category(name, name, items)


        shell = self._get_plugin("UI_Shell")

        w1, w2 = self.__browser.get_widgets()
        shell.set_sidebar(w1)
        shell.set_body(w2)



    def show(self):

        w1, w2 = self.__browser.get_widgets()
        w1.show_all()
        w2.show_all()


    def hide(self):

        w1, w2 = self.__browser.get_widgets()
        w1.hide()
        w2.hide()


    def set_location(self, expr):

        self.__browser.set_query(expr)



    def __on_activate(self, src, cmd, item):

        if (item):
            ci = ControlInspector(item)
            ci.show()
    

    def __search_handler(self, expr):

        status = self._get_plugin("Shell_StatusBar")
        try:
            matches = self.__collection.query(expr)
            status.set_status(_("Found %d controls.") % (len(matches)))
            matches.sort(lambda a,b: cmp(a.__name__, b.__name__))
        except:
            status.set_status(_("Invalid search expression."))
            matches = None
            
        return matches



    def __item_renderer(self, item):

        icon = os.path.join(self._get_path(), "control.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file(icon)
        name = item.__name__
        interfaces = Interface.get_interfaces(item)
        ifaces = []
        for i in interfaces:
            ifaces.append(Interface.get_id(i))

        return (pixbuf, name, "\n".join(ifaces))



    def __get_interfaces(self, collection):

        icon = os.path.join(self._get_path(), "interface.png")
        values = []
        matches = collection.query("(MATCH 'interface' '*')")
        for m in matches:
            values += [ (icon, Interface.get_id(iface),
                         "(MATCH 'interface' '%s')" % (Interface.get_id(iface)))
                        for iface in Interface.get_interfaces(m) ]

        return values



    def __get_alphabetically(self, collection):

        icon = os.path.join(self._get_path(), "folder.png")
        
        values = []
        
        for c in string.ascii_uppercase:
            query = "(MATCH 'name' '%c*')" % (c,)
            if collection.query( query ):
                values.append((icon, c, query))

        return values

        

def get_class(): return UI_ControlBrowser
