from shell.Plugin import Plugin
from shell.ItemBrowser import ItemBrowser
from main import HOME, USERHOME
from main.DisplayList import DisplayList
from utils import dialog

try:
    set
except NameError:
    from sets import Set as set

import gtk
import string
import gobject
import os
import textwrap


_DISPLAYLIST = os.path.join(USERHOME, "displays")
_DSPLIST = DisplayList(_DISPLAYLIST)

class UI_DisplayBrowser(Plugin):

    __PREVIEW_WIDTH = 48
    __NO_PREVIEW = os.path.join(HOME, "data", "gdesklets.png")


    def init(self):

        self.__location = ""
        self.__collection = self._get_plugin("Core_DisplayCollection")
        self.__collection.add_observer(self.__reload)
        self.__browser = ItemBrowser(self.__search_handler,
                                     self.__item_renderer,
                                     gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        self.__browser.add_observer(self.__on_activate)

        self.__reload()

        menu = self._get_plugin("UI_Menu")

        menu.set_item("File/Slot", gtk.STOCK_DELETE,
                      _("R_emove selected desklet"), self.__on_remove)
        menu.set_separator("File/Slot")
        menu.set_item("File/Slot", gtk.STOCK_EXECUTE,
                      _("_Run (remote) desklet..."), self.__on_run)
        menu.set_item("File/Slot", gtk.STOCK_EXECUTE,
                      _("R_un selected desklet"), self.__on_activate)

        shell = self._get_plugin("UI_Shell")

        w1, w2 = self.__browser.get_widgets()
        shell.set_sidebar(w1)
        shell.set_body(w2)

        profile = _DSPLIST.get_profile()
        self.__displays = _DSPLIST.get_displays(profile)


    def show(self):

        w1, w2 = self.__browser.get_widgets()
        w1.show_all()
        w2.show_all()


    def hide(self):

        w1, w2 = self.__browser.get_widgets()
        w1.hide()
        w2.hide()


    def set_location(self, expr):

        self.__location = expr
        self.__browser.set_query(expr)


    def __reload(self):

        for name, items in \
           [(_("by category"), self.__get_categories(self.__collection)),
            (_("by author"), self.__get_authors(self.__collection)),
            (_("alphabetically"), self.__get_alphabetically(self.__collection))]:
            self.__browser.add_category(name, name, items)


    def __on_run(self, *args):

        def responder(src, response):
            text = src.vbox.get_children()[0].get_children()[-1].get_text()
            if (response == gtk.RESPONSE_ACCEPT):
                if (text):
                    client = self._get_plugin("Core_Client")
                    ident = client.open_display(text)
                else:
                    src.destroy()

        from utils.HIGDialog import HIGDialog
        dialog = HIGDialog(buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.connect("response", responder)
        dialog.show()
        label = gtk.Label("Please enter a valid desklet URI here")
        label.show()
        entry = gtk.Entry()
        entry.show()

        vbox = dialog.vbox
        hbox = gtk.HBox()
        hbox.show()
        hbox.set_property("spacing", 12)
        hbox.set_property("border-width", 6)
        hbox.pack_start(label)
        hbox.pack_start(entry)
        vbox.pack_start(hbox)


    def __on_activate(self, *args):

        def run_old_one(*args):
        
            client.open_display_with_id(path, ident)

        def run_new_one(*args):

            client.open_display(path)


        found_display = False
        item = self.__browser.get_selected_item()
        if (item):
            client = self._get_plugin("Core_Client")
            path = os.path.abspath(item.path)

            if self.__displays:
                for ident in self.__displays:
                    saved_path = _DSPLIST.lookup_display(ident)[1]

                    if saved_path == path:
                        found_display = True
                        break

            if found_display is True:

                dialog.question(_("There is a saved instance of this display."),
                            _("Would you like to open this?"),
                            (gtk.STOCK_YES, run_old_one),
                            (gtk.STOCK_NO, run_new_one))
            
            else: run_new_one()


    def __on_remove(self, *args):

        def remove(*args):
            try:
                self.__remove_display(item.path)
            except OSError:
                dialog.warning(_("Could not remove"),
                               _("The desklet file could not be removed. "
                                 "This most likely means that you do not have "
                                 "write permission on it."))
            else:
                self.__collection.remove(item)
                self.set_location(self.__location)


        item = self.__browser.get_selected_item()
        if (item):
            dialog.question(None,
                            _("Do you really want to remove this desklet ?"),
                            _("The desklet will be removed from your system "
                              "and no longer be available."),
                            (gtk.STOCK_CANCEL, None),
                            (gtk.STOCK_DELETE, remove))



    def __search_handler(self, expr):

        status = self._get_plugin("Shell_StatusBar")
        try:
            matches = self.__collection.query(expr)
            status.set_status(_("Found %d desklets") % (len(matches)))
            matches.sort(lambda a,b: cmp(a.name, b.name))
        except:
            status.set_status(_("Invalid search expression."))
            matches = None

        self.__location = expr

        return matches



    def __item_renderer(self, item):

        path = item.path
        directory, filename = os.path.split(path)
        preview = item.preview.strip()
        if (preview): preview = os.path.join(directory, preview)
        name = item.name.strip() or os.path.splitext(filename)[0]
        version = item.version.strip() or "???"
        author = item.author.strip().replace("<", "&lt;") or "???"
        description = item.description.strip().replace("<", "&lt;") \
                      or _("No description available")
        description = "\n".join(textwrap.wrap(description, 66))

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(preview or self.__NO_PREVIEW)
        except:
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.__NO_PREVIEW)

        width, height = pixbuf.get_width(), pixbuf.get_height()
        scale = self.__PREVIEW_WIDTH / float(width)
        pixbuf = pixbuf.scale_simple(int(width * scale),
                                     int(height * scale),
                                     gtk.gdk.INTERP_BILINEAR)

        text = "<big><b>%(name)s</b></big> " \
               "<small>ver. %(version)s</small>\n" \
               "<small>%(path)s</small>\n" \
               "<i>by %(author)s</i>\n" \
               "%(description)s" % vars()

        return (pixbuf, text)



    def __get_categories(self, collection):

        icon = os.path.join(self._get_path(), "folder.png")
        values = []
        matches = collection.query("(MATCH 'category' '*')")
        categs = set([m.category for m in matches if m.category])
        for categ in categs:
            values += [(icon, c.strip(), "(MATCH 'category' '%s')" % c.strip())
                       for c in categ.split(",")]
        values += [(icon, "uncategorized", "(MATCH 'category' '')")]

        return values


    def __get_authors(self, collection):

        icon = os.path.join(self._get_path(), "author.png")
        values = []
        matches = collection.query("(MATCH 'author' '*')")
        authors = set([m.author for m in matches if m.author])
        for a in authors:
            values.append((icon, a, "(MATCH 'author' '%s')" % a))

        return values


    def __get_alphabetically(self, collection):

        icon = os.path.join(self._get_path(), "folder.png")
        values = []

        for c in string.ascii_uppercase:
            query = "(MATCH 'name' '%c*')" % (c,)
            if collection.query( query ):
                values.append((icon, c, query))
        for c in range(10):
            query = "(MATCH 'name' '%d*')" % c
            if collection.query( query ):
                values.append((icon, str(c), query))

        return values


    #
    # Removes the given .display file. If there are no .display files left
    # after, the whole directory gets removed.
    # Raises an OSError if it fails.
    #
    def __remove_display(self, path):

        def find(p):
            files = os.listdir(p)
            for f in files:
                filepath = os.path.join(p, f)
                if (os.path.isdir(f)): found = find(filepath)
                else: found = False

                if (found or (os.path.isfile(filepath) and
                      os.path.splitext(f)[-1] == ".display")):
                    return True
            #end for
            return False

        dirpath = os.path.dirname(path)

        # remove the given file
        os.remove(path)

        # if there are no .display files left, remove the directory
        if (not find(dirpath)):
            os.system("rm -rf %s" % (dirpath))


def get_class(): return UI_DisplayBrowser
