import gobject
import gtk
import re # just needed for parsing the widget descriptions
import logging

class WidgetList(gtk.VBox):
    ''' Forms a treeview list of desklets '''
    
    def __init__(self, main):
        ''' Creates the treeview for the right side (the actual view of the desklets). '''
        super(WidgetList, self).__init__(False, 6)
        
        # self.pack_start( TitleText( "Desklets", main.get_title_font_color()), False )

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
        
        # make it store the picture, name and description on the first level
        self.__tree_model = gtk.TreeStore(str, gtk.gdk.Pixbuf , str)
        
        self.tree_view = gtk.TreeView(self.__tree_model)
        self.__text_renderer = gtk.CellRendererText()
        self.__text_renderer.set_property("wrap-width", 400)
        pic_renderer = gtk.CellRendererPixbuf()
        installed_renderer = gtk.CellRendererToggle()
        
        pixbuf_column = gtk.TreeViewColumn('Icon')
        pixbuf_column.pack_start(pic_renderer, False)
        pixbuf_column.add_attribute(pic_renderer, 'pixbuf', 1)
        
        text_column = gtk.TreeViewColumn('Name')
        text_column.pack_start(self.__text_renderer, False)
        text_column.add_attribute(self.__text_renderer, 'markup', 2)
        text_column.set_sort_column_id(2)
        # text_column.set_resizable(True)
        
        # install_column = gtk.TreeViewColumn('Installed')
        # install_column.pack_start(installed_renderer, False)
        # install_column.add_attribute(installed_renderer, 'active', 3)
        # install_column.set_sort_column_id(3)
        
        self.tree_view.append_column(pixbuf_column)
        self.tree_view.append_column(text_column)
        # self.tree_view.append_column(install_column)
        # self.tree_view.get_selection().connect('cursor', self.selected_event)
        self.tree_view.connect('cursor-changed', self.selected_event)
        
        self.populate_treeview()
        
        
        
    def populate_treeview(self):
        max_size = 75
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
                asp = float(max_size) / cur_width
                target_height = asp * cur_height
                pixbuf = pixbuf.scale_simple(int(max_size), 
                                             int(target_height),
                                             gtk.gdk.INTERP_BILINEAR )
            else:
                asp = float(max_size) / cur_height
                target_width = asp * cur_width
                pixbuf = pixbuf.scale_simple(int(target_width),
                                             int(max_size),
                                             gtk.gdk.INTERP_BILINEAR )
        
            
            name = d_object.name
            
            # we have to rip out all tags from the description or we get very "funny" bugs
            # with descriptions switching places on the fly, etc. (just comment the re.sub to see)
            d_object.description = re.sub('<([^!>]([^>]|\n)*)>', '', d_object.description)
            
            d_object.pixbuf = pixbuf
            
            # deps = "<span weight=\"600\">Control Dependencies:</span> "
            # if len(d_object.dependencies) > 0:
            #     for dep in d_object.dependencies:
            #         deps += dep + ","
            #     deps = deps[0:-1] # strip last , 
            # else: 
            #     deps = ''
            # text =  "<big>"+name+"</big>"
            
            # install_state = False
            # if d_object.local_path is not None:
            #    install_state = True
            
            # check if the category row has been created
            cat = gobject.markup_escape_text(d_object.category)
            if category_paths.has_key(cat):
                self.__tree_model.append(category_paths[cat], (d_key, pixbuf, d_object.name) )
            else:
                category_paths[cat] = self.__tree_model.append(None, (None, None, cat))
                self.__tree_model.append(category_paths[cat], (d_key, pixbuf, d_object.name) )
            
        self.populate_controls()
        self.__scrolled_window.add(self.tree_view)
        
    
    
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
        # self.__text_renderer.set_property("wrap-width", w)
        
        
    
    def selected_event(self, event):
        if event is not None:
            selected = event.get_selection()
            treestore, treeiter = selected.get_selected()
            
            path  = treestore.get_path(treeiter)
            if len(path) == 1: # were talking about a category
                if self.tree_view.row_expanded(path): 
                    self.tree_view.collapse_row(path)
                else: self.tree_view.expand_row(path, False) 
                return
                
            desklet_key = treestore.get(treeiter, 0 )[0]
            #print "description:", treestore.get(treeiter, 2 )[0]
            desklet_object = self.__assembly.get_desklet(desklet_key)
            self.__selected_desklet = desklet_object
            self.__selected_desklet_iter = treeiter
            
        else:
            desklet_key = None
            self.__selected_desklet = None
        
        # self.refresh_view(self.__selected_desklet)    
        self.__main.desklet_selected_event(self.__selected_desklet)
        