''' DeskletBartender - the GTK-based simple interface to desklets management '''

import pygtk
import gtk
import gobject
import re # just needed for parsing the widget descriptions

import SexyShell.NewsView
import SexyShell.DeskletList

try:
    import gtkhtml2     # needed to render the news
    GTKHTML2_IS_AVAILABLE = True
except ImportError:
    GTKHTML2_IS_AVAILABLE = False

from Assembly import Assembly
from utils import log


class DeskletBartender(object):

    def __init__(self):

        self.__selected_desklet = None
        # try to find a default icon for the desklets that have no preview
        p = 'gfx/default_item_icon.png'
        self.__default_icon = gtk.gdk.pixbuf_new_from_file(p)

        # connect to the control and get the desklets
        self.__assembly = Assembly()
        self.__assembly.add_observer(self.assembly_event)


        self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.__window.set_title("Desklet Bartender")
        # HIG stuff
        self.__window.set_border_width(6)
        self.__window.set_default_size(700, 600)
        self.__window.connect("delete_event", self.close_window_event)

        # one vertical box to hold toolbars, and other boxes (not homogenous, 2px spacing)
        self.__top_box = gtk.VBox(False, 2)
        self.__window.add(self.__top_box)

        self.__construct_toolbar()

        self.__hpaned = gtk.HPaned()

        self.__top_box.pack_start(self.__hpaned)

        self.__statusbar = self.__construct_statusbar()
        self.__top_box.pack_start(self.__statusbar, False, False, 0)

        self.__window.show_all()

        # start the assembly
        self.__assembly.start()



    def __construct_toolbar(self):
        self.__action_group = gtk.ActionGroup("common")
        self.__action_group.add_actions([
                    ('install', gtk.STOCK_ADD, 'Install', None, 
                        'Install the selected widget', self.install_event), 
                    ('remove', gtk.STOCK_DELETE, 'Remove', None, 
                        'Remove the selected widget', self.remove_event ),
                    ('activate', gtk.STOCK_MEDIA_PLAY, 'Activate', None, 
                        'Activate the selected widget', self.activate_event), 
                    # Deactivating is not yet possible..
                    ('deactivate', gtk.STOCK_MEDIA_STOP, 'Deactivate', None, 
                        'Deactivate the selected widget', self.deactivate_event ),
                    ('update', gtk.STOCK_REFRESH, 'Update', None, 
                        'Update the widget list', self.update_event ),
                    ('quit', gtk.STOCK_QUIT, 'Quit', None, 'Quit the program', 
                        self.close_window_event)])
        toolbar = gtk.Toolbar()
        self.__action_group.get_action("install").set_sensitive(False)
        self.__action_group.get_action("remove").set_sensitive(False)
        self.__action_group.get_action("deactivate").set_sensitive(False)
        self.__action_group.get_action("activate").set_sensitive(False)

        toolbar.insert( self.__action_group.get_action("install").create_tool_item(), 0 )
        toolbar.insert( self.__action_group.get_action("remove").create_tool_item(), 1 )
        toolbar.insert( self.__action_group.get_action("activate").create_tool_item(), 2 )
        # toolbar.insert( self.__action_group.get_action("deactivate").create_tool_item(), 3 )
        # toolbar.insert( self.__action_group.get_action("update").create_tool_item(), 3 )
        toolbar.insert( self.__action_group.get_action("quit").create_tool_item(), 3 )

        self.__top_box.pack_start(toolbar, False)



    def __construct_statusbar(self):
        sb = gtk.Statusbar()
        sb.set_has_resize_grip(True)
        # create a stack of basic startup messages which can be easily popped while loading
        sb.push(0, 'All ready')
        sb.push(0, 'Building')
        sb.push(0, 'Looking for news')
        sb.push(0, 'Looking for local controls')
        sb.push(0, 'Looking for local desklets')
        sb.push(0, 'Looking for remote controls')
        sb.push(0, 'Looking for remote desklets')
        return sb


    def __construct_left_box(self):
        ''' Creates the smaller views for the right side of the box '''

        box = gtk.VBox(False, 2)

        if GTKHTML2_IS_AVAILABLE:
            newstitle = gtk.Label()
            newstitle.set_markup('<span size="xx-large" weight="bold">News</span>')
            box.pack_start(newstitle, False)

            newslabel = self.__construct_news_view()

            scrollwin = gtk.ScrolledWindow()
            scrollwin.set_size_request(250, -1)
            #scrollwin.set_width(300)
            scrollwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
            scrollwin.add(newslabel)
            box.pack_start(scrollwin)
        else:
            box.pack_start( gtk.Label("You need python-gtkhtml2 installed to view the news"))

        return box



    def __construct_news_view(self):
        news = self.__assembly.get_news()

        news_html = '<html><head></head><body style="background:white">'
        for n in news:
            news_html += '<div style="font-size:13px; text-decoration:underline">' \
                        + n['title'] + '</div> \n' + \
                        '<div>' \
                        + n['body'] + '</div> <hr />'
        news_html += '</body></html>'
        document = gtkhtml2.Document()
        # No event handlers at this time
        document.connect('request_url', self.request_url_event)
        document.connect('link_clicked', self.link_clicked_event)
        document.clear()
        document.open_stream('text/html')
        document.write_stream(news_html)
        document.close_stream()

        html_view = gtkhtml2.View()
        html_view.set_document(document)

        return html_view


    def __construct_right_box(self):
        ''' Creates the treeview for the right side (the actual view of the desklets). '''
        # make it store the picture, name and description on the first level
        self.__tree_model = gtk.ListStore(str, gtk.gdk.Pixbuf , str, bool)

        tree_view = gtk.TreeView(self.__tree_model)
        self.__text_renderer = gtk.CellRendererText()
        self.__text_renderer.set_property("wrap-width", 400)
        pic_renderer = gtk.CellRendererPixbuf()
        installed_renderer = gtk.CellRendererToggle()

        pixbuf_column = gtk.TreeViewColumn('Icon')
        pixbuf_column.pack_start(pic_renderer, False)
        pixbuf_column.add_attribute(pic_renderer, 'pixbuf', 1)

        text_column = gtk.TreeViewColumn('Description')
        text_column.pack_start(self.__text_renderer, False)
        text_column.add_attribute(self.__text_renderer, 'markup', 2)
        text_column.set_sort_column_id(2)
        # text_column.set_resizable(True)

        install_column = gtk.TreeViewColumn('Installed')
        install_column.pack_start(installed_renderer, False)
        install_column.add_attribute(installed_renderer, 'active', 3)
        install_column.set_sort_column_id(3)

        tree_view.append_column(pixbuf_column)
        tree_view.append_column(text_column)
        tree_view.append_column(install_column)
        tree_view.get_selection().connect('changed', self.desklet_view_selected_event)

        self.__treeview_scrollwin = gtk.ScrolledWindow()
        self.__treeview_scrollwin.set_border_width(6)
        self.__treeview_scrollwin.add(tree_view)
        self.__treeview_scrollwin.set_size_request(600, -1)
        self.__treeview_scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__treeview_scrollwin.connect("size-allocate", self.treeview_resize_event)

        # get the widgets and populate the treeview
        max_size = 75
        desklets = self.__assembly.get_desklets()
        # add desklets one by one to the tree model
        for d_key in desklets:
            d_object = desklets[d_key]
            # if there is a preview, scale it to a nice size
            if d_object.preview != '' and d_object.preview != None:
                pixbuf = gtk.gdk.pixbuf_new_from_file(d_object.preview)

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


            name = str(d_object.name)
            desc = str(d_object.description)

            # we have to rip out all tags from the description or we get very "funny" bugs
            # with descriptions switching places on the fly, etc. (just comment the re.sub to see)
            desc = re.sub('<([^!>]([^>]|\n)*)>', '', desc)

            deps = "<span weight=\"600\">Control Dependencies:</span> "
            if len(d_object.dependencies) > 0:
                for dep in d_object.dependencies:
                    deps += dep + ","
                deps = deps[0:-1] # strip last , 
            else: 
                deps = ''
            text =  "<big>"+name+"</big>"+"\n<i>"+desc+"</i>\n"+deps

            install_state = False
            if d_object.local_path is not None:
                install_state = True

            self.__tree_model.append((d_key, pixbuf, text, install_state) )


        return self.__treeview_scrollwin



    def __reset_textrenderer_width(self, w=None):
        if w is None:
            w = self.__treeview_scrollwin.size_request()[0] - 3000
        # self.__text_renderer.set_property("wrap-width", w)



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



    def update_event(self, event):
        log( "updating..." )



    def close_window_event(self, event, data=None):
        gtk.main_quit()



    def desklet_view_selected_event(self, event):
        if event is not None:
            treestore, treeiter = event.get_selected()
            desklet_key = treestore.get(treeiter, 0 )[0]
            #print "description:", treestore.get(treeiter, 2 )[0]
            desklet_object = self.__assembly.get_desklet(desklet_key)
            self.__selected_desklet = desklet_object
            self.__selected_desklet_iter = treeiter

        else:
            desklet_key = None
            self.__selected_desklet = None

        self.refresh_view(self.__selected_desklet)

        log( "selected ", desklet_key )



    def assembly_event(self, type, param):
        ''' Called by the assembly when something funky happens like the
            fetching is complete, something is installed or removed, etc.. '''
        log("assembly event has happened: %s - %s" % (type, param))

        if type == 'INSTALLED' or type == 'REMOVED':
            self.refresh_view(param)
        elif type == 'FETCH':
            print "fetch event", param
            self.__statusbar.pop(0)
            # All is done: construct the view
            if param == 'All done':
                print "All done..."
                lbox = self.__construct_left_box()
                rbox = self.__construct_right_box()
                self.__hpaned.add1( lbox )
                self.__hpaned.add2( rbox )
                self.__hpaned.show_all()


    def install_event(self, event):
        log(str( "install" + self.__selected_desklet.name ))
        self.__selected_desklet.install_newest_version()


    def remove_event(self, event):
        log(str( "remove" + self.__selected_desklet.name ))
        self.__selected_desklet.remove()


    def activate_event(self, event):
        log(str( "activate event " + self.__selected_desklet.name ))
        self.__selected_desklet.activate_all()


    def deactivate_event(self, event):
        log(str( "deactivate" + self.__selected_desklet.name ))
        self.__selected_desklet.deactivate()


    def link_clicked_event(self, event, param):
        print "link clicked with", event, param


    def request_url_event(self, event, param):
        print "url requested with", event


    def treeview_resize_event(self, event, param):
        #print "treeview resized", event, param.width
        self.__reset_textrenderer_width(param.width)



# make this directly runnable
if __name__ == '__main__':
    p = DeskletBartender()
    gtk.main()

