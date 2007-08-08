import gtk, logging

class PrefsDialog(gtk.Window):
    
    def __init__(self, main):
        super(PrefsDialog, self).__init__()
        # self.connect("delete_event", self.close_window_event)
        self.__main = main
        self.topbox = gtk.VBox(False, 6)
        self.set_title("Preferences")
        self.tooltips = gtk.Tooltips()
        self.tooltips.enable()
        
        self.add(self.topbox)
        # self.insert_text_option("A setting")
        self.insert_checkbox_option("gDesklets.org integration", 
                                    "Activate to automatically download the latest widgets from the website",
                                    self.website_integration_cb )
        self.insert_close_btn()
        self.show_all()
        
    
    def insert_text_option(self, text):
        b = gtk.HBox(False, 6)
        b.pack_start(gtk.Label(text), False, False, 6)
        e = gtk.Entry()
        e.connect('focus-out-event', self.changed_cb)
        b.pack_end(e, False, True, 6)
        self.topbox.pack_start(b, False, True, 6)
        
    
    def insert_checkbox_option(self, text, tool_tip=None, cb=None):
        b = gtk.CheckButton(text)
        if tool_tip is not None:
            self.tooltips.set_tip(b, tool_tip)
        b.connect('toggled', cb)
        self.topbox.pack_start(b, False, True, 6)
        
        
    def insert_close_btn(self):
        b = gtk.Button(None, gtk.STOCK_CLOSE)
        b.connect('pressed', self.close_btn_cb)
        self.topbox.pack_start(b, False, True, 6)
   
        
    def changed_cb(self, widget, *args):
        logging.info('PrefsDialog: changed_cb with %s arguments: %s' % (widget, args))
        
    
    def website_integration_cb(self, widget):
        print "website integation set to ", str( widget.get_active() )
        self.__main.set_website_integration(widget.get_active())
        
    def close_btn_cb(self, *args):
        self.destroy()
        
    # def close_window_event(self, *args):
    #    self.hide_all()