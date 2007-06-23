from shell.Plugin import Plugin
from main import ICON

import gtk

from utils import vfs


#
# The GUI shell where other plugins can plug into.
#
class UI_Shell(Plugin,):

    __TARGET_URL = 0
    __NETSCAPE_URL = 1

    # what we accept for drag & drop
    __DND_TYPES = [("text/uri-list", 0, __TARGET_URL),
                   ("x-url/http", 0, __NETSCAPE_URL),
                   ("_NETSCAPE_URL", 0, __NETSCAPE_URL)]


    def init(self):
        win = gtk.Window()
        win.set_title("gDesklets Shell")
        win.set_default_size(500, 300)
        win.connect("delete-event", self.__on_close)

        # set the icon
        win.set_icon(gtk.gdk.pixbuf_new_from_file(ICON))

        vbox = gtk.VBox()
        vbox.set_border_width(2)
        win.add(vbox)

        self.__menubox = gtk.HBox()
        vbox.pack_start(self.__menubox, False, False, 0)

        self.__toolbarbox = gtk.HandleBox()

        pane = gtk.HPaned()
        vbox.add(pane)

        lpane = gtk.VBox()
        pane.add1(lpane)

        self.__sidebarbox = gtk.HBox()
        lpane.pack_start(self.__sidebarbox, True, True, 0)

        self.__switchbox = gtk.HBox()
        lpane.pack_end(self.__switchbox, False, False, 0)

        self.__bodybox = gtk.HBox()
        pane.add2(self.__bodybox)

        self.__statusbox = gtk.HBox()
        vbox.pack_end(self.__statusbox, False, False, 0)

        win.show_all()

        menu = self._get_plugin("UI_Menu")
        menu.set_item("File", None, _("_File"), None)
        menu.set_slot("File/Slot")
        menu.set_separator("File/Separator")
        menu.set_item("File/Quit", gtk.STOCK_QUIT, "", self.__quit)

        menu.set_slot("Slot1")
        menu.set_slot("Slot2")

        plugins = self._get_plugins_by_pattern("name", "Shell_*")
        installer = self._get_plugin("Installer_Package")

        # set up drag & drop
        self.__bodybox.drag_dest_set(gtk.DEST_DEFAULT_ALL, self.__DND_TYPES,
                                     gtk.gdk.ACTION_COPY)
        self.__bodybox.connect("drag_data_received", self.__on_file_drop)



    def __on_file_drop(self, widget, context, x, y, data, info, time):

        files = [uri for uri in data.data.split("\r\n") if uri != '']
        installer = self._get_plugin("Installer_Package")

        if (info == self.__NETSCAPE_URL):
            for f in files:
                f, name = f.splitlines()[0:2]
                installer.install_from(f)
            #end for

        elif (info == self.__TARGET_URL):
            for f in files:
                if (f.startswith("file://")): f = f[7:]
                # filenames are URL-quoted
                installer.install_from(vfs.unescape_path(f))
            #end for



    def __on_close(self, src, event):

        self.__quit()


    def set_menu(self, widget):

        self.__menubox.add(widget)


    def set_toolbar(self, widget):

        self.__toolbarbox.add(widget)


    def set_switch(self, widget):

        self.__switchbox.add(widget)


    def set_sidebar(self, widget):

        self.__sidebarbox.add(widget)


    def set_body(self, widget):

        self.__bodybox.add(widget)


    def set_statusbar(self, widget):

        self.__statusbox.add(widget)


    def run(self):

        gtk.main()


    def __quit(self):

        gtk.main_quit()


def get_class(): return UI_Shell


try:
    import pygtk; pygtk.require("2.0")
except:
    pass

gtk.threads_init()

