from main import HOME

import gtk
import gobject



#
# Class for a list of items.
#
class ListView(gtk.TreeView):

    def __init__(self, columntypes, renderer):

        self.__items = {}
        self.__renderer = renderer


        gtk.TreeView.__init__(self)
        self.__liststore = gtk.ListStore(*columntypes)

        self.set_model(self.__liststore)
        self.set_headers_visible(False)

        cnt = 0
        for ctype in columntypes:
            if (ctype == gtk.gdk.Pixbuf):
                col = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(),
                                         pixbuf = cnt)
            elif (ctype == gobject.TYPE_STRING):
                col = gtk.TreeViewColumn(None, gtk.CellRendererText(),
                                         markup = cnt)
            
            self.append_column(col)
            cnt += 1
        #end for
            



    #
    # Clears the list.
    #
    def clear(self):

        self.__items = {}
        self.__liststore.clear()
        self.set_size_request(-1, -1)
        import gc; gc.collect()


    #
    # Returns the selected item or None.
    #
    def get_selected_item(self):

        path = self.get_cursor()[0]
        return self.__items.get(path)


    #
    # Selects the given item.
    #
    def select_item(self, item):

        for path, i in self.__items.items():
            if (item == i):
                self.set_cursor(path, None, False)
                break
        #end for



    #
    # Adds as item to the list.
    #
    def add_item(self, item):

        values = self.__renderer(item)

        iter = self.__liststore.append()
        for i in range(len(values)):
            self.__liststore.set(iter, i, values[i])

        path = self.__liststore.get_path(iter)
        self.__items[path] = item
