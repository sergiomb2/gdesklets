import gobject
import gtk
import re # just needed for parsing the widget descriptions
import logging

class WidgetList(gtk.VBox):
    ''' Forms a treeview list of desklets '''
    
    def __init__(self, main):
        ''' Creates the treeview for the right side (the actual view of the desklets). '''
        super(WidgetList, self).__init__(False, 6)
        
        self.__scrolled_window = gtk.ScrolledWindow()
        self.__scrolled_window.set_border_width(6)
        self.__scrolled_window.set_size_request(400, -1)
        self.__scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__scrolled_window.connect("size-allocate", self.resize_event)
        self.pack_start( self.__scrolled_window )
        
        # try to find a default icon for the desklets that have no preview
        p = 'gfx/default_item_icon.png'
        self.__default_icon = gtk.gdk.pixbuf_new_from_file(p)
        
        self.__main = main
        self.__assembly = main.get_assembly()
        
        txt_renderer = gtk.CellRendererText()
        button_renderer = gtk.CellRendererToggle()
        pic_renderer = gtk.CellRendererPixbuf()
        txt_renderer.set_property("wrap-width", 400)
        
        pixbuf_column = gtk.TreeViewColumn(_('Icon'))
        pixbuf_column.pack_start(pic_renderer, False)
        pixbuf_column.add_attribute(pic_renderer, 'pixbuf', 1)
        
        text_column = gtk.TreeViewColumn(_('Name'))
        text_column.pack_start(txt_renderer, False)
        text_column.add_attribute(txt_renderer, 'markup', 2)
        text_column.set_sort_column_id(2)
        text_column.set_resizable(True)
        
        installed_column = gtk.TreeViewColumn(_('Installed'))
        installed_column.set_alignment(0.0)
        button_renderer.xalign = 1.0
        installed_column.pack_start(button_renderer, False)
        installed_column.add_attribute(button_renderer, 'active', 3)
        
        # make it store the picture, name and description on the first level
        self.__tree_model = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, bool)
        self.populate_treemodel()
        
        self.tree_view = gtk.TreeView(self.__tree_model)
        self.tree_view.append_column(pixbuf_column)
        self.tree_view.append_column(text_column)
        self.tree_view.append_column(installed_column)
        
        self.tree_view.connect('cursor-changed', self.selected_event)
        self.tree_view.connect('row-activated', self.double_clicked_event)
        
        self.tree_view.enable_model_drag_dest([('text/plain', 0, 0)],
                  gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.tree_view.connect('drag-data-received', self.dnd_event)
        self.__scrolled_window.add(self.tree_view)
        
        # create the news section to the bottom
        # b = gtk.Button(_('News'))
        # self.pack_end(b, True, False, 6)
        
        
    def populate_treemodel(self):
        self.__tree_model.clear()
        desklets = self.__assembly.get_desklets()
        category_paths = {}
        
        # add desklets one by one to the tree model
        for d_key, d_object in desklets.items():            
            # if there is a preview, scale it to a nice size
            if d_object.preview != '' and d_object.preview != None:
                try: # some fail to load
                    pixbuf = gtk.gdk.pixbuf_new_from_file(d_object.preview)
                except:
                    pixbuf = self.__default_icon
            else:
                pixbuf = self.__default_icon
                
            cur_width = pixbuf.get_width()
            cur_height = pixbuf.get_height()
            if cur_width > cur_height:
                asp = 75.0 / cur_width
                target_height = asp * cur_height
                pixbuf = pixbuf.scale_simple(75, 
                                             int(target_height),
                                             gtk.gdk.INTERP_BILINEAR )
            else:
                asp = 75.0 / cur_height
                target_width = asp * cur_width
                pixbuf = pixbuf.scale_simple(int(target_width),
                                             75,
                                             gtk.gdk.INTERP_BILINEAR )
        
            d_object.pixbuf = pixbuf
            # we have to rip out all tags from the description or we get very "funny" bugs
            # with descriptions switching places on the fly, etc. (just comment the re.sub to see)
            d_object.description = re.sub('<([^!>]([^>]|\n)*)>', '', d_object.description)
            is_installed = d_object.local_path != None
                
            cat = gobject.markup_escape_text(d_object.category)
            if not category_paths.has_key(cat):
               category_paths[cat] = self.__tree_model.append(None, (None, None, cat, None))
           
            iter = self.__tree_model.append( category_paths[cat], (d_key, pixbuf, d_object.name, is_installed) )
            
        
    
    def refresh(self):
        logging.debug('WidgetList: refresh called')
        self.tree_view.queue_draw()
    
    
    def expand_all(self):
        self.tree_view.expand_all()
    
    
    def collapse_all(self):
        self.tree_view.collapse_all()
    
    
    def populate_controls(self):
        controls = self.__assembly.get_controls()
        category_paths = {}
        cat = self.__tree_model.append(None, (None, None, 'Controls'))
                
        for c_key, c_object in controls.items():            
            # we have to rip out all tags from the description or we get very "funny" bugs
            # with descriptions switching places on the fly, etc. (just comment the re.sub to see)
            c_object.description = re.sub('<([^!>]([^>]|\n)*)>', '', c_object.description)
            
            # check if the category row has been created
            self.__tree_model.append(cat, (c_key, self.__default_icon, c_object.name) )
       
    
    def resize_event(self, event, param): 
         #print "treeview resized", event, param.width
         # self.__reset_textrenderer_width(param.width)
         pass
    
    
    
    def __reset_textrenderer_width(self, w=None):
        if w is None:
            w = self.__treeview_scrollwin.size_request()[0] - 3000
        # txt_renderer.set_property("wrap-width", w)
        
        
    
    def double_clicked_event(self, treeview, path, view_column):
        # selected = event.get_selection()
        # treestore, treeiter = selected.get_selected()
        # path  = treestore.get_path(treeiter)
        
        if len(path) == 1: # were talking about a category
            if treeview.row_expanded(path): 
                treeview.collapse_row(path)
            else: 
                treeview.expand_row(path, False) 
            return
        
        treeiter = self.__tree_model.get_iter(path)
        desklet_key = self.__tree_model.get(treeiter, 0 )[0]
        desklet_object = self.__assembly.get_desklet(desklet_key)
        desklet_object.activate_all()
        self.__selected_widget = desklet_object
        self.__selected_widget_iter = treeiter
        
        self.__main.desklet_selected_event(self.__selected_widget)    
        
        
    
    def selected_event(self, event):
        if event is not None:
            selected = event.get_selection()
            treestore, treeiter = selected.get_selected()
            
            path  = treestore.get_path(treeiter)
            if len(path) == 1: # were talking about a category
            # this code enables opening categories on a single click.. 
            # albeit fast, it's a bit confusing for the users so let's turn it off
            #    if self.tree_view.row_expanded(path): 
            #        self.tree_view.collapse_row(path)
            #    else: self.tree_view.expand_row(path, False) 
                return
                
            desklet_key = treestore.get(treeiter, 0 )[0]
            #print "description:", treestore.get(treeiter, 2 )[0]
            desklet_object = self.__assembly.get_desklet(desklet_key)
            self.__selected_widget = desklet_object
            self.__selected_widget_iter = treeiter
            
        else:
            desklet_key = None
            self.__selected_widget = None
        
        self.__main.desklet_selected_event(self.__selected_widget)
        
        
    def dnd_event(self, widget, drag_context, x, y, sel_data, info, timestamp):
        print "DND EVENT HAPPENED -> ", sel_data.get_text()
        url = sel_data.get_text()
        self.__main.install_from_http(url) 
        
        
    def drop_cb(wid, context, x, y, time):
        print "DND DROP", wid, context
        context.finish(True, False, time)
        return True