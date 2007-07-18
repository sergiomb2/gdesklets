import gtk
import gobject

import WidgetList
import SideMenu
import MenuBar
import StatusBar
import PrefsDialog
import logging


class SlickShell(object):

    def __init__(self, assembly):
        
        self.__selected_desklet = None
        self.__assembly = assembly
        self.__assembly.add_observer(self.assembly_event)
        self.__construct_action_groups()
        self.__prefs_dialog = None
        
        self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.__window.set_title("Slick Shell")
        self.__window.connect("delete_event", self.close_window_event)
        self.__window.set_default_size(400, 400)
        
        # one vertical box to hold toolbars, and other boxes (not homogenous, 2px spacing)
        self.__top_box = gtk.VBox(False, 2)
        self.__window.add(self.__top_box)
        self.__status_bar = StatusBar.StatusBar()
        self.__top_box.pack_end(self.__status_bar, False, False, 0)
        self.__menubar = MenuBar.MenuBar(self)
        self.__top_box.pack_start(self.__menubar, False, False, 0)
        
        # the pane for the WidgetList and the newsview. will be filled
        # once the assembly has finished loading
        self.__hpaned = gtk.HPaned()
        self.__sidemenu = SideMenu.SideMenu(self)
        self.__hpaned.add2(self.__sidemenu)
        self.__top_box.pack_start(self.__hpaned)
        
        
        # self.__hpaned.add1(self.__side_menu)
        self.__active_widget = None # the widget that occupies the main view

        # self.__statusbar = StatusBar.StatusBar(self)
        # self.__top_box.pack_start(self.__statusbar, False, False, 0)
        
        self.__window.show_all()
        
        # start the assembly
        self.__assembly.start()
        
        
        
    def __construct_action_groups(self):
        ''' Actions are constructed here so that they are easily accessible by the
            other components '''
        self.__action_groups = {}
        self.__action_groups['global'] = gtk.ActionGroup("global")
        self.__action_groups['global'].add_actions([
                    ('update', gtk.STOCK_REFRESH, 'Update', None, 
                        'Update the widget list', self.update_event ),
                    ('quit', gtk.STOCK_QUIT, 'Quit', None, 'Quit the program', 
                        self.close_window_event),
                    ('about', gtk.STOCK_ABOUT, 'About', None, 'About gDesklets', 
                        self.show_about),
                    ('prefs', gtk.STOCK_PREFERENCES, 'Preferences', None, 'Set application preferences', 
                        self.show_prefs),
                    ])
        
        self.__action_groups['widget'] = gtk.ActionGroup("widget")
        self.__action_groups['widget'].add_actions([
                    ('install', gtk.STOCK_ADD, 'Install', None, 
                        'Install the selected widget', self.install_event), 
                    ('remove', gtk.STOCK_DELETE, 'Remove', None, 
                        'Remove the selected widget', self.remove_event ),
                    ('activate', gtk.STOCK_MEDIA_PLAY, 'Activate', None, 
                        'Activate the selected widget', self.activate_event), 
                    ])
                    
        self.__action_groups['widget'].get_action("install").set_sensitive(False)
        self.__action_groups['widget'].get_action("remove").set_sensitive(False)
        self.__action_groups['widget'].get_action("activate").set_sensitive(False)
        
        
        
    def refresh_view(self, event):
        ''' Refresh the view after installation, etc. '''
        desklet_object = self.__selected_desklet
        # print "refreshing because of ", desklet_object.name
        if desklet_object.local_path is not None:
            self.__action_group.get_action("remove").set_sensitive(True)
            self.__action_group.get_action("install").set_sensitive(False)
            self.__tree_model.set_value(self.__selected_desklet_iter, 3, True)
            # see if this is a desklet or a control and show the activate button
            try: 
                preview = desklet_object.preview
                self.__action_group.get_action("activate").set_sensitive(True)
            except:
                self.__action_group.get_action("activate").set_sensitive(False)
                
        else:
            self.__action_group.get_action("remove").set_sensitive(False)
            self.__action_group.get_action("install").set_sensitive(False)
            self.__action_group.get_action("activate").set_sensitive(False)
            self.__tree_model.set_value(self.__selected_desklet_iter, 3, False)
            
        if desklet_object.remote_domain is not None:
            self.__action_group.get_action("install").set_sensitive(True)
        else:
            self.__action_group.get_action("install").set_sensitive(False)
    
    
    def get_assembly(self): return self.__assembly

    
    
    def get_action_group(self, name): return self.__action_groups[name]



    def close_window_event(self, event, data=None):
        gtk.main_quit()


    
    def assembly_event(self, type, param):
        ''' Called by the assembly when something funky happens like the fetching is 
            complete, something is installed or removed, etc.. '''
        logging.info("assembly event has happened: %s - %s" % (type, param))
        
        if type == 'INSTALLED' or type == 'REMOVED': 
            self.refresh_view(param)
        elif type == 'FETCH':
            print "fetch event", param
            # self.__statusbar.pop(0)
            # All is done: construct the view
            if param == 'All done':
                self.__desklet_list = WidgetList.WidgetList(self)
                # self.__news_view = NewsView.NewsView(self)
                self.__hpaned.add1(self.__desklet_list)
                self.__hpaned.show_all()
                
    
        
    def install_event(self, event):
        logging.info("install" + self.__selected_desklet.name)
        self.__selected_desklet.install_newest_version()
    
    
    
    def remove_event(self, event):
        logging.info("remove" + self.__selected_desklet.name)
        self.__selected_desklet.remove()
        
        
    
    def activate_event(self, event):
        logging.info("activate event " + self.__selected_desklet.name)
        self.__selected_desklet.activate_all()
     
        
        
    def deactivate_event(self, event):
        logging.info("deactivate" + self.__selected_desklet.name)
        self.__selected_desklet.deactivate()
    
    
    def desklet_selected_event(self, desklet):
        # print desklet.remote_domain, "---", desklet.local_path
        if desklet.remote_domain is not None:
            self.__action_groups['widget'].get_action('install').set_sensitive(True)
        elif desklet.local_path is not None:
            self.__action_groups['widget'].get_action('remove').set_sensitive(True)
        else:
            self.__action_groups['widget'].get_action('install').set_sensitive(False)
            self.__action_groups['widget'].get_action('remove').set_sensitive(False)
        
        self.__sidemenu.show_desklet(desklet)
    
        
    def update_event(self, event):
        logging.info( "updating..." )
        
    def show_about(self, event):
        logging.info("showing the about window")
        ab = gtk.AboutDialog()
        ab.show_all()
  
    def show_prefs(self, event):
        logging.info("showing the preferences window")
        self.__prefs_dialog = PrefsDialog.PrefsDialog(self)
        