from GlassWindow import GlassWindow
from config.StateSaver import DefaultStateSaver
from utils.WindowSnapper import WindowSnapper
from layout import Unit
import utils
from main import ICON, UNSET_COORD

import gobject
import gtk


# the available window flags
_WINDOW_FLAG_NONE =      0
_WINDOW_FLAG_ABOVE =     1 << 0
_WINDOW_FLAG_BELOW =     1 << 1
_WINDOW_FLAG_STICKY =    1 << 2
_WINDOW_FLAG_MANAGED =   1 << 3
_WINDOW_FLAG_DECORATED = 1 << 4

# cursor mappings
_CURSORS = {
    "ARROW_RIGHT":       gtk.gdk.ARROW,
    "CROSSHAIR":         gtk.gdk.CROSSHAIR,
    "EDGE_N":            gtk.gdk.TOP_SIDE,
    "EDGE_S":            gtk.gdk.BOTTOM_SIDE,
    "EDGE_W":            gtk.gdk.LEFT_SIDE,
    "EDGE_E":            gtk.gdk.RIGHT_SIDE,
    "EDGE_NW":           gtk.gdk.TOP_LEFT_CORNER,
    "EDGE_NE":           gtk.gdk.TOP_RIGHT_CORNER,
    "EDGE_SW":           gtk.gdk.BOTTOM_LEFT_CORNER,
    "EDGE_SE":           gtk.gdk.BOTTOM_RIGHT_CORNER,
    "FLEUR":             gtk.gdk.FLEUR,
    "KILL":              gtk.gdk.PIRATE,
    "LINK":              gtk.gdk.HAND2,
    "POINTER_1":         gtk.gdk.LEFT_PTR,
    "POINTER_2":         gtk.gdk.RIGHT_PTR,
    "QUESTION":          gtk.gdk.QUESTION_ARROW,
    "TEXT":              gtk.gdk.XTERM,
    "WAIT":              gtk.gdk.WATCH,
    "X":                 gtk.gdk.X_CURSOR
    }


#
# Class for display windows.
#
class Window(GlassWindow):

    # there are four layers where desklet windows can be:
    #  - desktop layer (on the desktop behind all applications)
    #  - application layer (among the other applications)
    #  - floating layer (above all applications)
    #  - hidden layer (not visible)
    LAYER_DESKTOP = 0
    LAYER_APPLICATION = 1
    LAYER_FLOATING = 2
    LAYER_HIDDEN = 3

    # mapping: str -> window flag
    __WINDOW_FLAGS = {"below"  : _WINDOW_FLAG_BELOW,
                      "above"  : _WINDOW_FLAG_ABOVE,
                      "sticky" : _WINDOW_FLAG_STICKY,
                      "managed": _WINDOW_FLAG_MANAGED,
                      "decorated": _WINDOW_FLAG_DECORATED}

    __window_snapper = WindowSnapper()

    def __init__(self, display):

        # the current and original layer of the window
        self.__current_layer = self.LAYER_DESKTOP
        self.__original_layer = self.LAYER_DESKTOP

        # window bbox as it was stored in the window snapper
        self.__window_bbox = (0, 0, 0, 0)

        # the last mouse pointer position
        self.__last_pointer = (0, 0)

        # window position for detecting moves
        self.__window_pos = (UNSET_COORD, UNSET_COORD)

        # window size for detecting resizing
        self.__window_size = (0, 0)

        # the window flags
        self.__window_flags = _WINDOW_FLAG_NONE

        # the desktop borders
        self.__desktop_borders = (Unit.Unit(), Unit.Unit())

        # the current mouse cursor
        self.__cursor = None

        # whether we are in managed mode (window manager takes care of the
        # window); managed windows don't snap to desklets and cannot be moved
        # with the middle mouse button
        self.__managed_mode = False

        self.__float_mode = False

        # temporary data used for dragging windows
        self.__is_dragging = False
        self.__drag_offset = (0, 0)
        self.__dont_snap = False

        self.__shape = None

        GlassWindow.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_size_request(-1, -1)
        self.set_default_size(10, 10)

        # set the icon
        self.set_icon(gtk.gdk.pixbuf_new_from_file(ICON))

        self.__display = display


        display.show()
        self.add(display)
        display.add_observer(self.__on_observe_display)

        # set up event handlers
        self.connect("delete-event", self.__on_close)
        self.connect("key-press-event", self.__on_key, 0)
        self.connect("key-release-event", self.__on_key, 1)
        self.connect("button-press-event", self.__on_button, 0)
        self.connect("button-release-event", self.__on_button, True)
        self.connect("motion-notify-event", self.__on_motion, False)
        self.connect("leave-notify-event", self.__on_motion, True)
        self.connect("scroll-event", self.__on_scroll)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK |
                        gtk.gdk.POINTER_MOTION_MASK)
                        # POINTER_MOTION_HINT_MASK caused problems...
                        # gtk.gdk.POINTER_MOTION_HINT_MASK)

        self.realize()
        

    #
    # Observer handler for the display.
    #
    def __on_observe_display(self, src, cmd, *args):

        if (cmd == src.OBS_GEOMETRY):
            x, y, w, h = args
            if (x == UNSET_COORD or y == UNSET_COORD):
                # let the user place the window
                self.__begin_dragging()
            else:
                self.set_position(x, y, True)
                self.set_size(w, h)

        elif (cmd == src.OBS_BORDERS):
            x, y = args[0]
            self.__desktop_borders = (x, y)
            self.__set_struts()

        elif (cmd == src.OBS_FLAGS):
            flags = args[0]
            utils.request_call(self.__set_window_flags, flags)

        elif (cmd == src.OBS_ICON):
            icon = args[0]
            self.set_icon(icon)

        elif (cmd == src.OBS_SHAPE):
            shape = args[0]
            self.__set_shape(shape)

        elif (cmd == src.OBS_TITLE):
            title = args[0]
            self.set_title(title)

        elif (cmd == src.OBS_CURSOR):
            cursor = args[0]
            if (cursor):
                self.__cursor = gtk.gdk.Cursor(_CURSORS.get(cursor))
            else:
                self.__cursor = None

            self.window.set_cursor(self.__cursor)

        elif (cmd == src.OBS_CLOSED):
            wx, wy, w, h = self.__window_bbox
            self.__window_snapper.remove(wx, wy, w, h)
            self.destroy()
    


    #
    # Digs a hole into the window at the given position. This is necessary to
    # be able to place windows with embedded bonobo controls.
    #
    def __dig_a_hole(self, x, y):

        w, h = self.__window_size
        if (w != 0 and h != 0):
            mask = gtk.gdk.Pixmap(None, w, h, 1)
            gc = mask.new_gc()
            gc.foreground = gtk.gdk.Color(0, 0, 0, 1)
            mask.draw_rectangle(gc, True, 0, 0, w, h)
            gc.foreground = gtk.gdk.Color(0, 0, 0, 0)
            mask.draw_rectangle(gc, True, x - 4 , y - 4, 8, 8)
            self.get_children()[0].window.shape_combine_mask(mask, 0, 0)



    #
    # Begins a window dragging operation.
    #
    def __begin_dragging(self):

        assert(self.window)

        if (self.__is_dragging): return
        
        self.__is_dragging = True
        #self.update_observer(self.OBS_LOCK)
        x, y = self.get_pointer()
        w, h = self.__window_size
        w = max(5, w)
        h = max(5, h)
        if (not (0 <= x <= w)): x = max(1, w / 2)
        if (not (0 <= y <= h)): y = max(1, h / 2)
        self.__drag_offset = (x, y)
        self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))
        if (not self.__float_mode):
            self.__original_layer = self.__current_layer
            self.set_layer(self.LAYER_FLOATING)

        bx, by, bw, bh = self.__window_bbox
        if (not self.__managed_mode):
            self.__window_snapper.remove(bx, by, bw, bh)

        # grab the window focus to ensure that keypresses work
        self.present()

        gobject.timeout_add(50, self.__do_dragging)
        gobject.timeout_add(50, self.__do_move_window)

        return False



    #
    # Ends a window dragging operation.
    #
    def __end_dragging(self):

        assert(self.window)

        self.get_children()[0].window.shape_combine_mask(self.__shape, 0, 0)
        self.__is_dragging = False
        #self.update_observer(self.OBS_UNLOCK)
        self.window.set_cursor(self.__cursor)
        if (not self.__float_mode):
            self.set_layer(self.__original_layer)

        x, y = self.__window_pos
        w, h = self.__window_size
        if (not self.__managed_mode):
            self.__window_snapper.insert(x, y, w, h)

        self.__window_bbox = (x, y, w, h)
        self.__display.set_position(x, y)
        self.__set_struts()

        return False



    #
    # Drags the window.
    #
    def __do_dragging(self):

        if (self.__is_dragging):
            offx, offy = self.__drag_offset
            winx, winy = self.get_position()
            x, y = self.get_pointer()
            rx, ry = winx + x, winy + y

            if ((rx, ry) != self.__last_pointer):
                self.__last_pointer = (rx, ry)
                x += winx; y += winy
            else:
                wx, wy = self.__window_pos
                x = offx + wx; y = offy + wy

            new_x = x - offx
            new_y = y - offy
            if (self.__window_pos != (new_x, new_y)):
                if (not self.__dont_snap and not self.__managed_mode):
                    w, h = self.__window_size
                    new_x, new_y = self.__window_snapper.snap(new_x, new_y,
                                                              w, h)
                self.__window_pos = (new_x, new_y)

            return True

        else:
            return False



    def __do_move_window(self):

        x, y = self.__window_pos
        utils.request_call(self.move, x, y)

        return self.__is_dragging



    def __on_key(self, src, event, is_release):

        key = gtk.gdk.keyval_name(event.keyval)
        if (not is_release and self.__is_dragging):
            x, y = self.__window_pos

            # let the user move the display window with the keyboard
            if (key == "Left"): x -= 4
            elif (key == "Right"): x += 4
            elif (key == "Up"): y -= 4
            elif (key == "Down"): y += 4

            # stop dragging if the Return key is pressed
            elif (key == "Return"):
                self.__end_dragging()

            self.__window_pos = (x, y)

        if (not is_release):
            # don't snap while one of the SHIFT keys is pressed
            self.__dont_snap = (key in ("Shift_L", "Shift_R"))
        else:
            self.__dont_snap = False

        if (not self.__is_dragging):
            px, py = self.get_pointer()
            if (is_release):
                self.__display.send_event(self.__display.EVENT_KEY_RELEASE,
                                          key, px, py)
            else:
                self.__display.send_event(self.__display.EVENT_KEY_PRESS,
                                          key, px, py)
                                          


    def __on_motion(self, src, event, is_leave):

        if (self.__is_dragging): return

        if (is_leave):
            utils.request_call(self.__display.send_event,
                               self.__display.EVENT_LEAVE)
        else:
            utils.request_call(self.__display.send_event,
                               self.__display.EVENT_MOTION, event.x, event.y)



    def __on_button(self, src, event, is_release):

        # focus window when clicked; some window managers forget to do so
        self.present()
        
        if (not is_release and event.button == 2 and not self.__managed_mode):
            self.__begin_dragging()

        elif (not is_release and self.__is_dragging):
            self.__end_dragging()

        elif (is_release and self.__is_dragging):
            self.__end_dragging()

        px, py = self.get_pointer()
        if (is_release):
            self.__display.send_event(self.__display.EVENT_RELEASE,
                                      event.button, px, py)
        else:
            if (event.type == gtk.gdk._2BUTTON_PRESS):
                counter = 2
            else:
                counter = 1
                
            self.__display.send_event(self.__display.EVENT_PRESS,
                                      event.button, px, py, counter)


    def __on_scroll(self, src, event):

        px, py = self.get_pointer()
        self.__display.send_event(self.__display.EVENT_SCROLL, event.direction,
                                  px, py)


    def __on_close(self, src, *args):

        self.__display.close()
        return True


    #
    # Sets the current layer of the window.
    #
    def set_layer(self, layer):

        if (self.__current_layer == self.LAYER_HIDDEN != layer):
            self.show()
            
        self.__current_layer = layer

        if (layer == self.LAYER_DESKTOP):
            self._set_flag_above(False)
            self._set_flag_below(True)
            self._set_flag_managed(False)

        elif (layer == self.LAYER_APPLICATION):
            self._set_flag_above(False)
            self._set_flag_below(False)
            self._set_flag_managed(True)

        elif (layer == self.LAYER_FLOATING):
            self._set_flag_above(True)
            self._set_flag_below(False)
            self._set_flag_managed(False)

        elif (layer == self.LAYER_HIDDEN):
            self.hide()


    #
    # Toggles Float status of the window.
    #
    def set_float_mode(self, enabled):

        if (not self.__float_mode and enabled):
            self.__original_layer = self.__current_layer
            self.set_layer(self.LAYER_FLOATING)
            self.__float_mode = True

        elif (self.__float_mode and not enabled):
            self.set_layer(self.__original_layer)
            self.__float_mode = False



    #
    # Sets the position of the window. If dont_set is True, the display will not
    # be notified about the movement.
    #
    def set_position(self, x, y, dont_set = False):

        if (self.__window_pos != (x, y) and not self.__is_dragging):
            utils.request_call(self.move, x, y)
            self.__window_pos = (x, y)
            if (not dont_set): self.__display.set_position(x, y)

            bx, by, bw, bh = self.__window_bbox
            if (not self.__managed_mode):
                self.__window_snapper.remove(bx, by, bw, bh)
            w, h = self.__window_size
            if (not self.__managed_mode):
                self.__window_snapper.insert(x, y, w, h)

            self.__window_bbox = (x, y, w, h)
            self.__set_struts()
            gobject.timeout_add(0, self.show)




    #
    # Sets the size of the window.
    # 
    def set_size(self, width, height):

        if ((width, height) != self.__window_size):
            bx, by, bw, bh = self.__window_bbox

            if (not self.__managed_mode):
                self.__window_snapper.remove(bx, by, bw, bh)

            self.__window_size = (width, height)
            self.resize(width, height)

            if (not self.__managed_mode):
                self.__window_snapper.insert(bx, by, width, height)

            self.__window_bbox = (bx, by, width, height)
            self.__set_struts()
            



    #
    # Sets the window flags.
    #
    def __set_window_flags(self, value):

        is_managed = self.__managed_mode
        flags = _WINDOW_FLAG_NONE
        for p in value:
            p = p.strip()

            try:
                flags |= self.__WINDOW_FLAGS[p]
            except KeyError:
                log("Warning: %s is not a valid window flag." % (p,))


        # layers (above, below) in the "window-flags" property will become
        # deprecated in favor of a "layer" property
        if (not self.__float_mode and not self.__is_dragging):
            if (flags & _WINDOW_FLAG_BELOW):
                self.set_layer(self.LAYER_DESKTOP)
            elif (flags & _WINDOW_FLAG_ABOVE):
                self.set_layer(self.LAYER_FLOATING)
            else:
                self.set_layer(self.LAYER_APPLICATION)
                
        self._set_flag_sticky(flags & _WINDOW_FLAG_STICKY)
        #self._set_flag_managed(flags & _WINDOW_FLAG_MANAGED)
        self._set_flag_decorated(flags & _WINDOW_FLAG_DECORATED)
        self.__window_flags = flags

        # remove from window snapper
        if (not is_managed and flags & _WINDOW_FLAG_MANAGED):
            self.__managed_mode = True
            bx, by, bw, bh = self.__window_bbox
            self.__window_snapper.remove(bx, by, bw, bh)

        # insert into window snapper
        elif (is_managed and not flags & _WINDOW_FLAG_MANAGED):
            self.__managed_mode = False
            bx, by, bw, bh = self.__window_bbox
            self.__window_snapper.insert(bx, by, bw, bh)



    #
    # Sets the window's shape.
    #
    def __set_shape(self, mask):

        self.__shape = mask
        if (not self.__is_dragging):
            self.shape_combine_mask(mask, 0, 0)



    #
    # Sets desktop struts.
    #
    def __set_struts(self):

        border_x, border_y = self.__desktop_borders
        bx, by, bw, bh = self.__window_bbox
        border_x.set_100_percent(bw)
        border_y.set_100_percent(bh)
        b_x = border_x.as_px()
        b_y = border_y.as_px()
        
        x, y, w, h = self.__window_bbox

        if (not border_x.is_unset()):
            deskwidth = gtk.gdk.screen_width()
            leftstrut = x + w
            rightstrut = deskwidth - x
            left = (leftstrut < rightstrut) and leftstrut + b_x or 0
            right = (leftstrut > rightstrut) and rightstrut + b_x or 0
        else:
            left = right = 0

        if (not border_y.is_unset()):
            deskheight = gtk.gdk.screen_height()
            topstrut = y + h
            bottomstrut = deskheight - y
            top = (topstrut < bottomstrut) and topstrut + b_y or 0
            bottom = (topstrut > bottomstrut) and bottomstrut + b_y or 0
        else:
            top = bottom = 0

        self.window.property_change("_NET_WM_STRUT", "CARDINAL", 32,
                             gtk.gdk.PROP_MODE_REPLACE,
                             [left, right, top, bottom])
