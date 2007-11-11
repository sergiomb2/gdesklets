import gtk, logging

class PrefsDialog(gtk.Window):
    
    def __init__(self, main, config):
        super(PrefsDialog, self).__init__()
        # self.connect("delete_event", self.close_window_event)
        self.__main = main
        
        self.win_layout = gtk.VBox()
        
        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(6)
        
        # general settings page
        self.general_settings_page = gtk.VBox()
        self.set_title(_("gDesklets Preferences"))
        self.tooltips = gtk.Tooltips()
        self.tooltips.enable()
        self.notebook.append_page(self.general_settings_page) # , _('General'))
        
        self.win_layout.pack_start(self.notebook, True, True, 6)
        
        btnbox = gtk.HBox()
        btn = gtk.Button(None, gtk.STOCK_CLOSE)
        btn.connect('pressed', self.close_btn_cb)
        btnalign = gtk.Alignment(1.0, 0.5, 0.5, 1.0)
        btnalign.add(btn)
        self.win_layout.pack_start(btnalign, True, True, 6)
        
        self.add(self.win_layout)
        # self.insert_text_option("A setting")
        self.insert_checkbox_option(_("gDesklets.org integration"), 
                                    _("Activate to automatically download the latest widgets from the website"),
                                    self.website_integration_cb, config.get('website_integration') )
        self.insert_checkbox_option(_("Expand categories on startup"), 
                                    _("Display all the widgets inside the categories on startup"),
                                    self.expand_tabs_cb, config.get('expand_tabs_by_default') )
        self.show_all()
        
    
    def insert_text_option(self, text):
        b = gtk.HBox(False, 6)
        b.pack_start(gtk.Label(text), False, False, 6)
        e = gtk.Entry()
        e.connect('focus-out-event', self.changed_cb)
        b.pack_end(e, False, True, 6)
        self.general_settings_page.pack_start(b, False, True, 6)
        
    
    def insert_checkbox_option(self, text, tool_tip, cb, value):
        b = gtk.CheckButton(text)
        print "---------------> ", value
        b.set_active(int(value))
        if tool_tip is not None:
            self.tooltips.set_tip(b, tool_tip)
        b.connect('toggled', cb)
        self.general_settings_page.pack_start(b, False, True, 6)
        
             
    def changed_cb(self, widget, *args):
        logging.info('PrefsDialog: changed_cb with %s arguments: %s' % (widget, args))
        
    
    def website_integration_cb(self, widget):
        self.__main.set_website_integration(widget.get_active())
    
    
    def expand_tabs_cb(self, widget):
        self.__main.set_expand_tabs(widget.get_active())
        
        
    def close_btn_cb(self, *args):
        self.destroy()
        
    # def close_window_event(self, *args):
    #    self.hide_all()