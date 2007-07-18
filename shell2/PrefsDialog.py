import gtk, logging

class PrefsDialog(gtk.Window):
    
    def __init__(self, main):
        super(PrefsDialog, self).__init__()
        # self.connect("delete_event", self.close_window_event)
        self.topbox = gtk.VBox()
        self.add(self.topbox)
        self.insert_text_option("A setting")
        self.insert_text_option("Another setting")
        self.show_all()
        
    
    def insert_text_option(self, text):
        b = gtk.HBox()
        b.pack_start(gtk.Label(text))
        e = gtk.Entry()
        e.connect('focus-out-event', self.changed_cb)
        b.pack_end(e)
        self.topbox.pack_start(b)
        
        
    def changed_cb(self, widget, event, *args):
        logging.info('PrefsDialog: changed_cb with %s' % widget)
        
        
    # def close_window_event(self, *args):
    #    self.hide_all()