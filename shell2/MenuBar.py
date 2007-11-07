import gtk

# TODO: the *_menu.append() calls here cause a GTK assertion failure
# in the form of "GtkWarning: gtk_accel_label_set_accel_closure: assertion 
# `gtk_accel_group_from_accel_closure (accel_closure) != NULL' failed"
# the exact reason is the create_menu_item-call, but I can't figure why

class MenuBar(gtk.MenuBar):
    
    def __init__(self, main):
        super(MenuBar, self).__init__()
        self.__main = main
        ac = main.get_action_group('global')
        
        file_menu = gtk.Menu()
        file_mitem = gtk.MenuItem("_File")
        file_mitem.set_submenu(file_menu)
        file_menu.append(ac.get_action('quit').create_menu_item())
        
        edit_menu = gtk.Menu()
        edit_mitem = gtk.MenuItem("_Edit")
        edit_mitem.set_submenu(edit_menu)
        edit_menu.append(ac.get_action('update').create_menu_item())
        edit_menu.append(ac.get_action('prefs').create_menu_item())
        
        help_menu = gtk.Menu()
        help_mitem = gtk.MenuItem("_Help")
        help_mitem.set_submenu(help_menu)
        help_menu.append(ac.get_action('about').create_menu_item())
        
        self.append(file_mitem)
        self.append(edit_mitem)
        self.append(help_mitem)
        
        
        