from BookmarkList import BookmarkList
from ListView import ListView
from SearchBar import SearchBar
from utils.Observable import Observable


try:
    set
except NameError:
    from sets import Set as set
    
import gtk


#
# Class for item browser widgets.
#
class ItemBrowser(Observable):

    OBS_ACTIVATE_ITEM = 0


    def __init__(self, search_handler, item_renderer, *columns):

        self.__search_handler = search_handler

        # build bookmarks list
        self.__bookmarks = BookmarkList()
        self.__browser = gtk.VBox()

        # build search bar
        self.__searchbar = SearchBar()
        self.__searchbar.show_all()
        self.__searchbar.add_observer(self.__on_search)
        self.__browser.pack_start(self.__searchbar, False, False, 0)

        # build list view
        scrwin = gtk.ScrolledWindow()
        scrwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__browser.pack_end(scrwin, True, True, 0)

        self.__list = ListView(columns, item_renderer)
        self.__list.connect("row-activated", self.__on_activate_item)
        scrwin.add(self.__list)


    #
    # Returns the widgets.
    #
    def get_widgets(self):

        return (self.__bookmarks, self.__browser)


    #
    # Adds a category to the bookmarks list.
    #
    def add_category(self, name, label, items):

        self.__bookmarks.add_category(name, name)

        items = list(set(items))
        items.sort(lambda a,b: cmp(a[1], b[1]))
        for icon, label, expr in items:
            if (icon):
                pixbuf = gtk.gdk.pixbuf_new_from_file(icon)
            else:
                pixbuf = None
            
            self.__bookmarks.add_item(name, pixbuf, label,
                                      self.__on_select_entry, expr)
        #end for
        
        self.__bookmarks.select_category(0) 


    #
    # Sets a search query manually.
    #
    def set_query(self, expr):
        
        self.__searchbar.set_query(expr)


    #
    # Returns the currently selected item.
    #
    def get_selected_item(self):

        return self.__list.get_selected_item()
    

    def __on_select_entry(self, expr):

        self.set_query(expr)


    def __on_search(self, src, cmd, expr):
        assert (self.__search_handler)
        
        self.__list.clear()
        matches = self.__search_handler(expr)

        if (matches):
            for item in matches:
                self.__list.add_item(item)

        return matches


    def __on_activate_item(self, *args):

        item = self.__list.get_selected_item()
        self.update_observer(self.OBS_ACTIVATE_ITEM, item)
