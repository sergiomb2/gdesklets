from utils import wallpaper
from utils.BGWatcher import BGWatcher
from utils.tiling import Tiling

import gobject
import gtk
import cairo
import sys

try:
    from utils import x11
except ImportError:
    import sys
    log("Could not import x11 module!")
    sys.exit(1)


#
# Class for transparent windows.
#
class GlassWindow(gtk.Window):

    #
    # Constructor.
    #
    def __init__(self, wintype = gtk.WINDOW_TOPLEVEL):

        # handler for transparency updates
        self.__update_handler = None

        # remember the current window position to detect movements
        self.__position = (0, 0)
        self.__size = (0, 0)

        # window manager
        self.__wm = self.__get_window_manager()

        gtk.Window.__init__(self, wintype)

        self.__layout = gtk.Fixed()
        self.__layout.show()
        gtk.Window.add(self, self.__layout)

        self.__background = Tiling()
        self.__layout.put(self.__background, 0, 0)
        
        self.__on_screen_changed (self, None)
        self.set_app_paintable (True)
        
        self.__bg_watcher = BGWatcher()

        self.connect("configure-event", self.__on_configure)
        self.connect("screen-changed", self.__on_screen_changed)
        self.connect("expose-event", self.__on_expose_event)
        self.connect("composited-changed", self.__on_composited_changed)
        
        self.__is_composited = True
        self.__on_composited_changed (self)



    #
    # Override add method.
    #
    def add(self, widget):

        self.__layout.put(widget, 0, 0)



    #
    # Override resize method.
    #
    def resize(self, width, height):

        self.__layout.set_size_request(width, height)
        gobject.idle_add(gtk.Window.resize, self, width, height)



    #
    # Observer method for the background.
    # Connect this method to the BG watcher.
    #
    def __bg_observer(self, src, cmd):

        self.__update_bg()



    #
    # Updates the background for transparency.
    #
    def __update_bg(self):

        if (self.__update_handler):
            gobject.source_remove(self.__update_handler)
            self.__update_handler = gobject.timeout_add(100, self.__updater)
        else: self.__updater()



    def __updater(self):

        if (not self.window): return

        x, y = self.window.get_origin()
        width, height = self.window.get_size()
        if (width > 1 and height > 1):
            self.__capture_bg(x, y, width, height)



    #
    # Captures the background to create transparency.
    #
    def __capture_bg(self, x, y, width, height):

        wallpaper.get_wallpaper(self.__background, x, y, width, height)
        self.queue_draw()

    #
    # Reacts on expose event
    #
    def __on_expose_event (self, widget, event = None, user_data = None):

        cr = widget.window.cairo_create ()
        cr.set_source_rgba (1.0, 1.0, 1.0, 0.0)
        cr.set_operator (cairo.OPERATOR_SOURCE)
        cr.paint ()

    #
    # Reacts on composited changed
    #
    def __on_composited_changed (self, widget):
        
        screen = self.get_screen ()
        is_composited = gtk.ver[1] >= 10 and screen.is_composited ()
        
        if self.__is_composited == is_composited:
            return
        
        if is_composited:
            self.__is_composited = True
            self.__background.hide ()
            try:
                self.__bg_watcher.remove_observer(self.__bg_observer)
            except: pass
        else:
            self.__is_composited = False
            self.__bg_watcher.add_observer(self.__bg_observer)
            self.__background.show ()

    #
    # Reacts on screen changed
    #
    def __on_screen_changed (self, src, old_screen):
        
        screen = self.get_screen ()
        colormap = screen.get_rgba_colormap ()
        
        if colormap == None:
            colormap = screen.get_rgb_colormap ()

        self.set_colormap (colormap)


    #
    # Reacts on moving the window.
    #
    def __on_configure(self, src, event):

        pos = self.window.get_origin()
        size = self.window.get_size()
        if (pos != self.__position or size != self.__size):
            self.__position = pos
            self.__size = size
            if not self.__is_composited: 
                self.__update_bg()


    #
    # Sets the BELOW window flag.
    #
    def _set_flag_below(self, value, tries = 0):

        if (not self.__wm == "Enlightenment" and
            not self.get_property("visible") and
            not tries >= 10):
            gobject.timeout_add(500, self._set_flag_below, value, tries + 1)

        if (self.window):
            x11.set_above(self.window, not value)
            x11.set_below(self.window, value)



    #
    # Sets the ABOVE window flag.
    #
    def _set_flag_above(self, value, tries = 0):

        if (not self.__wm == "Enlightenment" and
            not self.__wm.startswith("Xfwm4") and
            not self.get_property("visible") and
            not tries >= 11):
            gobject.timeout_add(500, self._set_flag_above, value, tries + 1)

        if (self.window):
            x11.set_below(self.window, not value)
            x11.set_above(self.window, value)



    #
    # Sets the STICKY window flag.
    #
    def _set_flag_sticky(self, value):

        if (value): self.stick()
        else: self.unstick()



    def _set_type_hint_dock(self, window, value):

        x11.set_type_dock(window, value)



    #
    # Sets the MANAGED window flag.
    #
    def _set_flag_managed(self, value):

        if (value):
            self.set_property("skip-taskbar-hint", 0)
            self.set_property("skip-pager-hint", 0)
            self._set_type_hint_dock(self.window, False)
        else:
            self.set_property("skip-taskbar-hint", 1)
            self.set_property("skip-pager-hint", 1)

            if (self.__wm == "Metacity"):
                self._set_type_hint_dock(self.window, True)



    #
    # Sets the DECORATED window flag.
    #
    def _set_flag_decorated(self, value):

        if (value): self.set_decorated(True)
        else: self.set_decorated(False)



    #
    # Returns the name of the running EWMH compliant window manager or "".
    #
    def __get_window_manager(self):

        name = ""
        win = ""
        # get the window where the EMWH compliant window manager tells its name
        root = gtk.gdk.get_default_root_window()
        try:
            ident = root.property_get("_NET_SUPPORTING_WM_CHECK", "WINDOW")[2]
            win = gtk.gdk.window_foreign_new(long(ident[0]))
        except TypeError, exc:
            log("Your window manager doesn't support "
                "_NET_SUPPORTING_WM_CHECK! Switch to a compliant WM!"
                "The following error occurred:\n%s" % (exc,))
        if (win != None and win != ""):
            try:
                name = win.property_get("_NET_WM_NAME")[2]
            except TypeError, exc:
                log("Your window manager doesn't support _NET_WM_NAME!\n"
                    "Switch to a EWMH compliant WM.\n"
                    "The following error occurred:\n%s" % (exc,))
                return name

        return name

