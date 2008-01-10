from ConfigWidget import ConfigWidget
from utils.datatypes import *

import gtk


class ConfigList(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__items_values = []

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("items", TYPE_LIST, self._setp_items,
                                self._getp, [],
                                doc = "List of (label, value) items")

        self._register_property("value", TYPE_LIST, self._setp_value,
                                self._getp, [],
                                doc = "Current selection")



    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        value = self._get_config()

        self.__mainbox = gtk.VBox(False, 0)
        self.__scrolledwindow=gtk.ScrolledWindow()
        self.__scrolledwindow.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)

        self.__liststore = gtk.ListStore(bool, str, str)
        self.__listview = gtk.TreeView(self.__liststore)
        self.__listview.set_headers_visible(False)
        self.__listview.show()
        self.__scrolledwindow.add(self.__listview)
        self.__scrolledwindow.show()
        self.__mainbox.pack_start(self.__scrolledwindow, True, True, 3)

        selection = self.__listview.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.connect("changed", self.__on_change)


        self.tvcolumn = gtk.TreeViewColumn()
        self.__listview.append_column(self.tvcolumn)
        self.togglecell = gtk.CellRendererToggle()
        self.tvcolumn.pack_start(self.togglecell, True)
        self.tvcolumn.add_attribute(self.togglecell, "active", 0)
        self.togglecell.connect("toggled", self.__on_toggled, self.__liststore)
        self.togglecell.set_property("activatable", True)
        self.togglecell.set_property("visible", True)
        self.itemcell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.itemcell, True)
        self.tvcolumn.add_attribute(self.itemcell, "text", 1)
        self.valuecell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.valuecell, True)
        self.tvcolumn.add_attribute(self.valuecell, "text", 2)
        self.valuecell.set_property("visible", False)

        self.selectbox = gtk.EventBox()
        self.selectlabel = gtk.Label("Unknown selection...")
        self.selectbox.add(self.selectlabel)
        self.selectbox.set_property("visible", True)
        self.selectlabel.show()
        self.selectbox.show()
        self.selectbox.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.selectbox.connect("button-press-event", self.menu_popup)

        self.__mainbox.pack_start(self.selectbox, True, True, 3)
        self.__mainbox.show()

        # add menus to the text under the list to allow quick selection
        self.menu = gtk.Menu()
        sel_all = gtk.MenuItem("Select all", False)
        sel_none = gtk.MenuItem("Select none", False)
        sel_tog = gtk.MenuItem("Toggle selection", False)
        sel_all.connect("activate", self.select_all)
        sel_none.connect("activate", self.select_none )
        sel_tog.connect("activate", self.toggle_selection)
        self.menu.append(sel_all)
        self.menu.append(sel_none)
        self.menu.append(sel_tog)
        sel_all.show()
        sel_none.show()
        sel_tog.show()

        return (align, self.__mainbox)


    def _set_enabled(self, value):

        self.__listview.set_sensitive(value)


    def _set_label(self, value):

        self.__label.set_text(value)
        

    def __on_change(self, src):

        selection = []
        model, paths = src.get_selected_rows()
        if paths:
          item = self.__liststore.get_iter_first()
          if (self.__items_values):
              while item:
                  path = self.__liststore.get_path(item)
                  if self.__liststore[path][0]:
                      selection.append(self.__liststore[path][2])
                  item = self.__liststore.iter_next(item)
              self._setp("value", selection)

        self._set_config(selection)
        self.update_selection_label()


    def __on_toggled(self, cell, path, model):

        model[path][0] = not model[path][0]
        self.update_selection_label()


# menu functions:
# selection: select_all, select_none and toggle_selection
# popup: menu_popup

    def select_all(self, widget):
        item = self.__liststore.get_iter_first()
        while item:
            path = self.__liststore.get_path(item)
            self.__liststore[path][0] = True
            item = self.__liststore.iter_next(item)
        self.__on_change(self.__listview.get_selection())


    def select_none(self, widget):
        item = self.__liststore.get_iter_first()
        while item:
            path = self.__liststore.get_path(item)
            self.__liststore[path][0] = False
            item = self.__liststore.iter_next(item)
        self.__on_change(self.__listview.get_selection())


    def toggle_selection(self, widget):
        item = self.__liststore.get_iter_first()
        while item:
            path = self.__liststore.get_path(item)
            self.__liststore[path][0] = not self.__liststore[path][0]
            item = self.__liststore.iter_next(item)
        self.__on_change(self.__listview.get_selection())


    def menu_popup(self, widget, event):
        if event.button == 3:
            self.menu.popup(None, None, None, 0, 0)

# end menu functions


    def __get_selection_num(self):

        selected = available = 0
        item = self.__liststore.get_iter_first()
        while item:
            available += 1
            path = self.__liststore.get_path(item)
            if self.__liststore[path][0]:
                selected += 1
            item = self.__liststore.iter_next(item)
        return selected, available


    def update_selection_label(self):

        selected, available = self.__get_selection_num()
        self.selectlabel.set_text("Selected "+str(selected)+" of "+str(available)+" items")


    def _setp_items(self, key, items):

        self.__items_values = []
        self.__listview.get_model().clear()
        for k, v in items:
            self.__liststore.append([False, str(k), str(v)])
            self.__items_values.append(v)
        #end for

        self._setp(key, items)
        self.set_prop("value", self.get_prop("value"))
        # show min. 4 and max. 8 rows
        w, h = self.__listview.size_request()
        if len(items) < 4: newheight = 4*h/len(items)
        elif len(items) > 8: newheight = 8*h/len(items)
        else: newheight = h
        self.__scrolledwindow.set_size_request(-1, newheight)
        self.__scrolledwindow.resize_children()
        self._set_selection('value', self._getp('value'))


    def _set_selection(self, key, value):

        item = self.__liststore.get_iter_first()
        while item:
          path = self.__liststore.get_path(item)
          for v in value:
            if str(v) == str(self.__liststore[path][2]):
              self.__liststore[path][0] = True
          item = self.__liststore.iter_next(item)
             

    def _setp_value(self, key, value):

        print "key: "+str(key)
        print "Value: "+str(value)
        
        try:
            index = self.__items_values.index(value)
        except:
            index = 0

        self.__listview.set_cursor(index)
        self.__listview.scroll_to_cell(index)
        self._set_config(value)
        self._setp(key, value)
