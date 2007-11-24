import gtk


class SideMenu(gtk.EventBox):
    
    def __init__(self, main):
        super(SideMenu, self).__init__()
        self.set_size_request(200, -1)
        self.__main = main
        self.modify_bg(gtk.STATE_NORMAL,
                       gtk.gdk.color_parse("black"))
        self.__box = gtk.VBox(False, 6)
        self.add(self.__box)
        
        # set the logo. FIXME: is gtk.Image deprecated?
        logo = pixbuf = gtk.gdk.pixbuf_new_from_file('gfx/logo.png')
        self.__image = gtk.Image()
        self.__image.set_from_pixbuf(logo)
        self.__box.pack_start(self.__image)
        
        self.__info_name = gtk.Label()
        self.__info_name.set_markup("<big>gDesklets</big>")
        self.__info_name.set_line_wrap(True)
        self.__info_name.modify_fg(gtk.STATE_NORMAL, 
                         gtk.gdk.color_parse("white"))
        
        self.__info_desc = gtk.Label()
        self.__info_desc.set_markup("<i>Desktop Eyecandy</i>")
        self.__info_desc.modify_fg(gtk.STATE_NORMAL, 
                         gtk.gdk.color_parse("white"))
        self.__info_desc.set_line_wrap(True)
        
        box = gtk.VBox()
        box.pack_start(self.__info_name)
        box.pack_start(self.__info_desc)
        align = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
        align.set_padding(6,6,6,6)
        align.add(box)
        self.__box.pack_start(align, expand=True)
        
        ac_group = self.__main.get_action_group('widget')
        install_btn = ac_group.get_action('install').create_tool_item()
        remove_btn = ac_group.get_action('remove').create_tool_item()
        activate_btn = ac_group.get_action('activate').create_tool_item()
        activate_btn.set_expand(True)
        
        tb = gtk.Toolbar()
        tb.insert(activate_btn, 0)
        tb.insert(install_btn, 1)
        tb.insert(remove_btn, 2)
        # tb.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.__box.pack_end(tb, True, True)
        
        # news, desklets, controls buttons
        #news_icon = gtk.Image()
        #news_icon.set_from_file("SexyShell/gfx/news32x32.png")
        
        #desklet_icon = gtk.Image()
        #desklet_icon.set_from_file("SexyShell/gfx/desklet32x32.png")
        
        #control_icon = gtk.Image()
        #control_icon.set_from_file("SexyShell/gfx/control32x32.png")
        
        #pixbuf = self.render_icon(gtk.STOCK_ADD, gtk.ICON_SIZE_LARGE_TOOLBAR)
        #install_icon = gtk.Image()
        #install_icon.set_from_pixbuf(pixbuf)
        #pixbuf = self.render_icon(gtk.STOCK_DELETE, gtk.ICON_SIZE_LARGE_TOOLBAR)
        #remove_icon = gtk.Image()
        #remove_icon.set_from_pixbuf(pixbuf)
        #pixbuf = self.render_icon(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_LARGE_TOOLBAR)
        #activate_icon = gtk.Image()
        #activate_icon.set_from_pixbuf(pixbuf)
        
        
        #align = gtk.Alignment(0.5, 0.4, 0, 0)
        #align.add(self.__install_menu)
        #self.pack_start(align)
        #self.set_widget_menu_buttons(False, False, False)
        
        # a separator
        # self.pack_start( gtk.HSeparator() )
        
    
    def show_desklet(self, desklet):
        self.__info_name.set_markup(desklet.name)
        try: 
            self.__info_desc.set_markup(desklet.description)
        except: 
            self.__info_desc.set_markup("No description")
        self.__image.set_from_pixbuf(desklet.pixbuf)
        self.show_all()
        
        