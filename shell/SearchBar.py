from utils.Observable import Observable

import gtk


class SearchBar(gtk.HBox, Observable):

    OBS_UPDATE = 0
    

    def __init__(self):

        gtk.HBox.__init__(self, False, 4)
        self.set_border_width(4)

        self.__query = gtk.Entry()
        self.__query.connect("key-press-event", self.__on_key)
        self.pack_start(self.__query, True, True, 0)

        searchbtn = gtk.Button(_("Search"))
        searchbtn.connect("clicked", self.__on_click, self.__query)
        self.pack_end(searchbtn, False, False, 0)



    def set_query(self, query):

        self.__query.set_text(query)
        self.update_observer(self.OBS_UPDATE, query)
        

    def __on_key(self, src, event):

        key = gtk.gdk.keyval_name(event.keyval)
        if (key in ("Return", "KP_Enter")):
            self.update_observer(self.OBS_UPDATE, src.get_text())



    def __on_click(self, src, query):

        self.update_observer(self.OBS_UPDATE, query.get_text())
