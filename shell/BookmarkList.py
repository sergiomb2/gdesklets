from shell.ListView import ListView

import gtk
import gobject


class BookmarkList(gtk.VBox):

    def __init__(self):

        self.__entries = []
        self.__categories = {}
        self.__category_names = []

        gtk.VBox.__init__(self)
        self.__listview = ListView((gtk.gdk.Pixbuf, gobject.TYPE_STRING),
                                   self.__item_renderer)
        self.__listview.connect("cursor-changed", self.__on_select_item)

        self.__optmenu = gtk.combo_box_new_text()
        self.__optmenu.connect("changed", self.__on_select_category)
        self.pack_start(self.__optmenu, False, False, 4)

        scrwin = gtk.ScrolledWindow()
        scrwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrwin.add(self.__listview)
        self.pack_end(scrwin, True, True, 0)
        
        self.show_all()


    def select_category(self, n):

        self.__optmenu.set_active(n)
        


    def add_category(self, name, label):

        if (name in self.__categories):
            self.clear_category(name)
        else:
            self.__optmenu.append_text(name)
            self.__categories[name] = []
            self.__category_names.append(name)
        


    def add_item(self, category, icon, label, callback, *args):
        assert (category in self.__categories)

        self.__categories[category].append((icon, label, callback, args))


    def clear_category(self, category):
        assert (category in self.__categories)

        self.__categories[category] = []


    def __on_select_item(self, src):

        path, col = src.get_cursor()
        callback, args = self.__entries[path[0]]
        if (callback): callback(*args)


    def __on_select_category(self, src):

        index = self.__optmenu.get_active()
        name = self.__category_names[index]
        items = self.__categories[name]
        self.__listview.clear()
        self.__entries = []
        for i in items:
            icon, label, callback, args = i
            self.__listview.add_item((icon, label))
            self.__entries.append((callback, args))
        #end for

    def __item_renderer(self, item):

        icon, label = item
        label = label.replace("<" ,"&lt;")
        return (icon, label)
