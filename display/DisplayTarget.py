from layout import Unit
from layout.LayoutObject import LayoutObject
from utils.datatypes import *
from utils.Struct import Struct
from DataTarget import DataTarget

from urllib import unquote

import utils

import gobject
import gtk


#
# Abstract class for DisplayTargets.
#
class DisplayTarget(DataTarget):

    __slots__ = ('__layout_object', '_geometry_lock', '__anchor',
                 '__had_action', '__action_stamp', '__pushed_cursor')

    # observer actions
    OBS_GEOMETRY = 0

    # user actions
    ACTION_CLICK = "click"
    ACTION_DOUBLECLICK = "doubleclick"
    ACTION_PRESS = "press"
    ACTION_RELEASE = "release"
    ACTION_MENU = "menu"
    ACTION_SCROLL = "scroll"
    ACTION_ENTER = "enter"
    ACTION_LEAVE = "leave"
    ACTION_MOTION = "motion"
    ACTION_FILE_DROP = "file-drop"
    ACTION_LINK_DROP = "link-drop"
    ACTION_KEY_PRESS = "key-press"
    ACTION_KEY_RELEASE = "key-release"

    # placement anchors
    ANCHOR_NW = "nw"
    ANCHOR_N = "n"
    ANCHOR_NE = "ne"
    ANCHOR_E = "e"
    ANCHOR_SE = "se"
    ANCHOR_S = "s"
    ANCHOR_SW = "sw"
    ANCHOR_W = "w"
    ANCHOR_CENTER = "center"

    # what we accept for drag & drop
    __DND_FILE = [("text/uri-list", 0, 0)]
    __DND_LINK = [("x-url/http", 0, 0), ("_NETSCAPE_URL", 0, 0)]


    def __init__(self, name, parent):

        # the action stamp helps us to detect ENTER and LEAVE events
        self.__action_stamp = 0
        # the queue of actions
        self.__action_queue = []

        # the layout object
        self.__layout_object = parent.new_layout_object()
        self.__layout_object.set_callback(self.__geometry_callback)
        self.__layout_object.set_action_callback(self.__action_callback)

        # the currently pushed mouse cursor
        self.__pushed_cursor = None

        # lock for geometry computations
        self._geometry_lock = True

        # the placement anchor
        self.__anchor = self.ANCHOR_NW

        # the value of the last notify_handle_action call
        self.__had_action = False

        DataTarget.__init__(self, name, parent)

        for prop, datatype in [("x", TYPE_UNIT),
                               ("y", TYPE_UNIT),
                               ("width", TYPE_UNIT),
                               ("height", TYPE_UNIT)]:
            self._register_property(prop, datatype,
                                    self._setp_geometry, self._getp_geometry)
        self.set_prop("x", Unit.ZERO)
        self.set_prop("y", Unit.ZERO)
        self.set_prop("width", Unit.Unit())
        self.set_prop("height", Unit.Unit())

        self._register_property("relative-to", TYPE_LIST,
                                self._setp_relative_to, self._getp)

        self._register_property("anchor", TYPE_STRING,
                                self._setp_anchor, self._getp)

        self._register_property("cursor", TYPE_STRING,
                                self._setp_cursor, self._getp)

        self._register_property("menu", TYPE_OBJECT,
                                self._setp_menu, None)

        self._register_property("visible", TYPE_BOOL,
                                self._setp_visible, self._getp)
        self._setp("visible", True)

        for action in (self.ACTION_ENTER,
                       self.ACTION_LEAVE,
                       self.ACTION_CLICK,
                       self.ACTION_PRESS,
                       self.ACTION_RELEASE,
                       self.ACTION_SCROLL,
                       self.ACTION_FILE_DROP,
                       self.ACTION_LINK_DROP,
                       self.ACTION_DOUBLECLICK,
                       self.ACTION_MOTION,
                       self.ACTION_MENU,
                       self.ACTION_KEY_PRESS,
                       self.ACTION_KEY_RELEASE):
            self._register_action(action)



    #
    # Creates and returns a new layout object as a child of this element's
    # layout object.
    #
    def new_layout_object(self):

        return self.__layout_object.new_child()



    #
    # Returns the layout object of this element.
    #
    def get_layout_object(self):

        return self.__layout_object



    #
    # Callback handler for changes in the geometry.
    #
    def __geometry_callback(self, src, x, y, w, h):

        self.get_widget().set_size_request(w.as_px(), h.as_px())
        utils.request_call(self.update_observer, self.OBS_GEOMETRY)



    #
    # Callback handler for user actions.
    #
    def __action_callback(self, src, x, y, stamp, action, event):

        self.detect_enter(stamp)

        call = self.get_action_call(action)
        if (call):
            self.__action_queue.append((action, x, y, event))
            utils.request_idle_call(self.__process_actions)



    #
    # Processes the remaining actions.
    #
    def __process_actions(self):

        while (self.__action_queue):
            action, x, y, event = self.__action_queue.pop()
            self.handle_action(action, x, y, event)



    #
    # Detects and emits ENTER events.
    #
    def detect_enter(self, stamp):

        if (not self.__action_stamp):
            # send enter event
            action = self.ACTION_ENTER
            if (self.get_action_call(action)):
                self.handle_action(action, Unit.ZERO, Unit.ZERO, Struct())

            # change cursor
            cursor = self._getp("cursor")
            if (cursor):
                self._get_display().push_cursor(cursor)
                self.__pushed_cursor = cursor

        self.__action_stamp = stamp



    #
    # Detects and emits LEAVE events.
    #
    def detect_leave(self, stamp):

        if (self.__action_stamp and stamp != self.__action_stamp):
            self.__action_stamp = 0
            # send leave event
            action = self.ACTION_LEAVE

            if (self.get_action_call(action)):
                self.handle_action(action, Unit.ZERO, Unit.ZERO, Struct())

            # revert cursor
            if (self.__pushed_cursor):
                self._get_display().pop_cursor(self.__pushed_cursor)
                self.__pushed_cursor = None



    def _is_active(self): return (self.__action_stamp != 0)



    def __on_file_drop(self, widget, context, x, y, data, info, time):
        ''' catch DND events and process them to send them to them
        main display, which forwards them to the sensor '''

        # get the display
        display = self._get_display()

        # tell the main display to send files and coordinates to the sensor
        files = [unquote(uri) for uri in data.data.split("\r\n") if uri != '']
        display.send_action(self, self.ACTION_FILE_DROP,
                            Struct(files = files, _args = [files]))



    def __on_link_drop(self, widget, context, x, y, data, info, time):
        ''' catch DND events and process them to send them to them
        main display, which forwards them to the sensor '''

        # get the display
        display = self._get_display()

        # tell the main display to send link and coordinates to the sensor
        links = [unquote(data.data.split("\n")[0])]
        display.send_action(self, self.ACTION_LINK_DROP,
                            Struct(links = links, _args = [links]))



    #
    # Returns whether this target is standalone, i.e. needs no parent.
    #
    def is_standalone(self): return False



    #
    # Returns the widget of this target.
    #
    def get_widget(self): raise NotImplementedError



    #
    # Returns the true coordinates of this target when the given coordinates
    # are the hotspot.
    #
    def get_anchored_coords(self, x, y, w, h):
        assert (isinstance(x, Unit.Unit))
        assert (isinstance(y, Unit.Unit))
        assert (isinstance(w, Unit.Unit))
        assert (isinstance(h, Unit.Unit))

        if (x.is_unset() or y.is_unset()):
            return (x, y)

        anchor = self.__anchor
        if (anchor in (self.ANCHOR_NW, self.ANCHOR_W, self.ANCHOR_SW)):
            ax = x
        elif (anchor in (self.ANCHOR_N, self.ANCHOR_CENTER, self.ANCHOR_S)):
            ax = x - (w / 2)
        else:
            ax = x - w

        if (anchor in (self.ANCHOR_NW, self.ANCHOR_N, self.ANCHOR_NE)):
            ay = y
        elif (anchor in (self.ANCHOR_W, self.ANCHOR_CENTER, self.ANCHOR_E)):
            ay = y - (h / 2)
        else:
            ay = y - h

        return (ax, ay)



    #
    # Returns the geometry (coordinates and size) of this target.
    #
    def get_geometry(self):

        x, y, w, h = self.__layout_object.get_real_geometry()
        if (self.get_prop("visible")):
            return (x, y, w, h)
        else:
            return (x, y, Unit.ZERO, Unit.ZERO)



    #
    # Returns the geometry from the user's point of view.
    #
    def get_user_geometry(self):

        return self.__layout_object.get_geometry() #self.__user_geometry



    #
    # Sets the position of this target.
    #
    def set_position(self, x, y):
        assert (isinstance(x, Unit.Unit))
        assert (isinstance(y, Unit.Unit))

        ox, oy, w, h = self.__layout_object.get_geometry()
        if ((x, y) != (ox, oy)):
            self.__layout_object.set_geometry(x = x, y = y)



    #
    # Sets the size of this target. Use this instead of set_size_request() in
    # targets to set the size manually.
    #
    def set_size(self, width, height):
        assert (isinstance(width, Unit.Unit))
        assert (isinstance(height, Unit.Unit))

        x, y, w, h = self.__layout_object.get_geometry()
        if ((w, h) != (width, height)):
            if (w.get_unit() != Unit.UNIT_PERCENT):
                self.__layout_object.set_geometry(width = width)
            if (h.get_unit() != Unit.UNIT_PERCENT):
                self.__layout_object.set_geometry(height = height)



    def handle_action(self, action, px, py, event):
        assert (isinstance(px, Unit.Unit))
        assert (isinstance(py, Unit.Unit))

        # we need the pointer position relative to the widget, so we have to
        # setup a new event structure for some actions
        if (action in (self.ACTION_CLICK, self.ACTION_DOUBLECLICK,
                       self.ACTION_MOTION, self.ACTION_PRESS,
                       self.ACTION_RELEASE)):
            x, y = self.get_widget().get_pointer()
            nil, nil, w, h = self.get_geometry()
            ux = Unit.Unit(x, Unit.UNIT_PX)
            uy = Unit.Unit(y, Unit.UNIT_PX)
            if (w.as_px() > 0): ux.set_100_percent(w.as_px())
            if (h.as_px() > 0): uy.set_100_percent(h.as_px())
            event["x"] = ux
            event["y"] = uy
            # FIXME: remove eventually :)
            if (action == self.ACTION_MOTION): event["_args"] = [x, y]

        DataTarget.handle_action(self, action, px, py, event)



    #
    # Geometry properties.
    #
    def _setp_geometry(self, key, value):
        assert (isinstance(value, Unit.Unit))

        if (key == "x"):
            self.__layout_object.set_geometry(x = value)
            self._setp(key, value)

        elif (key == "y"):
            self.__layout_object.set_geometry(y = value)
            self._setp(key, value)

        elif (key == "width"):
            self.__layout_object.set_geometry(width = value)
            self._setp(key, value)

        elif (key == "height"):
            self.__layout_object.set_geometry(height = value)
            self._setp(key, value)



    def _setp_relative_to(self, key, value):

        name, mode = value
        if (mode == "x"): rx, ry = True, False
        elif (mode == "y"): rx, ry = False, True
        elif (mode == "xy"): rx, ry = True, True
        else: rx, ry = False, False

        def f():
            try:
                parent = self._get_parent()
                my_id = self._getp("id")

                if (not parent or not parent.get_child_by_id(my_id)):
                    return

                obj = self._get_parent().get_child_by_id(name)

                # if it is not a child of our parent and not the parent itself, something is wrong
                if (not obj and not (parent._getp("id") == name)):
                    raise UserError(_("Element \"%s\" does not exist") % name,
                                   _("The <tt>relative-to</tt> property "
                                     "requires a reference to an existing "
                                     "display element within the same parent "
                                     "container."))

                # FIXME ?! So far 'relative-to' only works for "siblings".
                #          Would a 'relative-to' parents make any sense ?!
                if obj:
                    relative = obj.get_layout_object()
                    self.__layout_object.set_relative_to(relative, rx, ry)
            except:
                import traceback; traceback.print_exc()
                pass

        # we have to delay because the relative might not be available at that
        # time
        utils.request_call(f)

        self._setp(key, value)



    def _setp_anchor(self, key, value):

        self.__anchor = value
        if (value in (self.ANCHOR_NW, self.ANCHOR_W, self.ANCHOR_SW)):
            ax = 0.0
        elif (value in (self.ANCHOR_N, self.ANCHOR_CENTER, self.ANCHOR_S)):
            ax = 0.5
        else:
            ax = 1.0

        if (value in (self.ANCHOR_NW, self.ANCHOR_N, self.ANCHOR_NE)):
            ay = 0.0
        elif (value in (self.ANCHOR_W, self.ANCHOR_CENTER, self.ANCHOR_E)):
            ay = 0.5
        else:
            ay = 1.0

        self.__layout_object.set_anchor(ax, ay)
        self._setp(key, value)



    def _getp_geometry(self, key):

        x, y, w, h = self.__layout_object.get_real_geometry()

        if (key == "x"):
            unit = x
        elif (key == "y"):
            unit = y
        elif (key == "width"):
            unit = w
        elif (key == "height"):
            unit = h

        return unit



    #
    # "visible" property.
    #
    def _setp_visible(self, key, value):

        if (value): self.get_widget().show()
        else: self.get_widget().hide()
        self.__layout_object.set_enabled(value)
        self._setp(key, value)


    #
    # "menu" property.
    #
    def _setp_menu(self, key, value):

        dsp = self._get_display()
        utils.request_call(dsp.open_menu, value)



    #
    # Action handlers.
    #
    def _setp__action(self, key, value):

        DataTarget._setp__action(self, key, value)
        if (key == "on-file-drop"):
            self.get_widget().drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                            self.__DND_FILE,
                                            gtk.gdk.ACTION_COPY)
            self.get_widget().connect("drag_data_received",
                                      self.__on_file_drop)

        elif (key == "on-link-drop"):
            self.get_widget().drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                            self.__DND_LINK,
                                            gtk.gdk.ACTION_COPY)
            self.get_widget().connect("drag_data_received",
                                      self.__on_link_drop)



    #
    # "cursor" property.
    #
    def _setp_cursor(self, key, value):

        self._setp(key, value)
        if (self.__pushed_cursor):
            self._get_display().pop_cursor(self.__pushed_cursor)
            self._get_display().pop_cursor(value)
            self.__pushed_cursor = value


    #
    # Unlocks the initial lock for geometry computations.
    # By locking the geometry engine initially, we can build up the display
    # without redundant geometry computations. The necessary computations are
    # done once when unlocking.
    #
    def unlock_geometry(self):

        self._geometry_lock = False



    #
    # Returns whether the geometry engine is locked.
    #
    def _is_geometry_locked(self):

        return self._geometry_lock

