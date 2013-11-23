from layout.LayoutObject import LayoutObject
from config.DisplayConfigger import DisplayConfigger
from config.StateSaver import DefaultStateSaver
from DisplayConfigurator import DisplayConfigurator
from DisplayTarget import DisplayTarget
from TargetGroup import TargetGroup
from MenuItem import MenuItem
from main import UNSET_COORD
from scripting.Script import Script
from scripting.Scriptlet import Scriptlet
from utils import actionparser
from utils.Struct import Struct
from utils.Observable import Observable
from utils.HIGDialog import HIGDialog
from layout import Unit
from utils import vfs

import targetregistry
import utils
import utils.dialog

import gobject
import gtk
import time
import random
import sys
import os
import re
import gc

try:
    from utils.tiling import Tiling
except ImportError:
    log("Could not import tiling module!")
    sys.exit(1)


# The name of the namespace where all display element are accessible.

_ROOT = "Dsp"


#
# Class for display windows.
#
class Display(gtk.HBox, Observable):

    __slots__ = ('__sensor_controls', '__arrays',
                 '__group', '__script',
                 '__configurator', '__path', '__display_file', '__id',
                 '__last_pointer_pos', '__pointer_pos', '__is_sensitive',
                 '__cursor_stack')

    # observer commands
    OBS_CLOSE = 0
    OBS_RESTART = 1
    OBS_GEOMETRY = 2
    OBS_SHAPE = 3
    OBS_TITLE = 4
    OBS_ICON = 5
    OBS_FLAGS = 6
    OBS_BORDERS = 7
    OBS_CURSOR = 8
    OBS_CLOSED = 9
    OBS_DISABLE = 10


    # event types
    EVENT_MOTION = 0
    EVENT_PRESS = 1
    EVENT_RELEASE = 2
    EVENT_KEY_PRESS = 3
    EVENT_KEY_RELEASE = 4
    EVENT_LEAVE = 5
    EVENT_SCROLL = 6


    # regular expression to test whether a path is absolute
    __IS_ABSOLUTE_PATH_RE = re.compile("[a-zA-Z]+://.+")

    def __init__(self, ident, rep):

        self.__action_stamp = 1

        # the display menu
        self.__DISPLAY_MENU = [
            MenuItem("/__cfg", _("_Configure desklet"),
                     callback = self.__handle_configure,
                     icon = gtk.STOCK_PREFERENCES),
            MenuItem("/__move", _("_Move desklet"),
                     callback = self.__handle_move),
            MenuItem("/__sep1"),
            MenuItem("/__src", _("_View Source"),
                     callback = self.__handle_source,
                     icon = gtk.STOCK_EDIT),
            MenuItem("/__sep2"),
            MenuItem("/__restart", _("Re_start desklet"),
                     callback = self.__handle_restart,
                     icon = gtk.STOCK_REDO),
            MenuItem("/__remove", _("_Remove desklet"),
                     callback = self.__handle_remove,
                     icon = gtk.STOCK_DELETE),
            MenuItem("/__remove", _("_Disable desklet"),
                     callback = self.__handle_disable,
                     icon = gtk.STOCK_CLOSE),
            MenuItem("/__sep3"),
            MenuItem("/__about", _("_About"),
                     callback = self.__handle_about,
                     icon = gtk.STOCK_ABOUT)
            ]

        # the layout object
        self.__layout_object = LayoutObject(None)

        self.__menu = []

        self.__swindow = []

        # the stack of current mouse cursors
        self.__cursor_stack = []

        # the controls handling the deprecated sensor stuff: id -> control
        self.__sensor_controls = {}

        # mapping of the elements to their parent arrays: child_id -> array_id
        self.__arrays = {}

        # content of this display (valid until display has been initialized)
        self.__content = None

        # scriptlets of this display (valid until display has been initialized)
        self.__scriptlets = []

        # the root TargetGroup
        self.__group = None

        # the scripting environment
        self.__script = Script(ident, rep)

        # the path of the .display file
        self.__path = os.path.dirname(rep)
        self.__display_file = rep

        # the configurator object
        self.__configurator = DisplayConfigger(ident, self.__path)
        self.__configurator.set_scripting_environment(self.__script)

        # the about window
        self.__about = gtk.AboutDialog()
        self.__about.set_wrap_license(True)
        self.__about.connect("response", self.__about_response_callback)
        self.__about.connect("close", self.__about_close_and_delete_callback)
        self.__about.connect("delete_event",
                              self.__about_close_and_delete_callback)

        # the readme window
        self.__readme = HIGDialog(buttons = (gtk.STOCK_CLOSE,
                                             gtk.RESPONSE_CLOSE), self_destroy = False)
        self.__readme.set_title("%s - README" % os.path.basename(rep))

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_IN)
        textview = gtk.TextView()
        textview.set_editable(False)
        textview.set_overwrite(False)
        textview.set_left_margin(8)
        textview.set_right_margin(8)
        textview.set_wrap_mode(gtk.WRAP_WORD)
        textview.set_cursor_visible(False)
        textview.set_size_request(500, 300)
        self.__readme_buffer = textview.get_buffer()
        sw.add(textview)
        sw.show()
        self.__swindow.append(sw)

        textview.show()
        self.__readme.vbox.add(sw)
        self.__readme.connect("response", self.__readme_response_callback)
        self.__readme.connect("close", self.__readme_close_and_delete_callback)
        self.__readme.connect("delete_event",
                              self.__readme_close_and_delete_callback)

        # the unique ID of this display
        self.__id = ident

        # the last position of the mouse pointer (used for filtering out
        # unwanted events)
        self.__last_pointer_pos = (-1, -1)

        # mapping between sensors and targets; which target watches
        # which sensor?
        # (sensor, port) -> (target, property)
        self.__mapping = {}

        # temporary data for remembering the position of the last mouse click
        self.__pointer_pos = (0, 0)

        # whether the display reacts on events
        self.__is_sensitive = True

        gtk.HBox.__init__(self)



    #
    # Returns the unique ID of this display.
    #
    def get_id(self): return self.__id

    def get_next_child_index(self): return -1

    def get_index_path(self): return []



    #
    # Initializes the display. Call this after you have finished constructing
    # it.
    #
    def initialize(self):
        assert self.__content

        childtype, settings, children = self.__content

        # load saved positions
        positions = DefaultStateSaver().get_key("positions", {})
        lx, ly = positions.get(self.get_id(), (UNSET_COORD, UNSET_COORD))
        x = settings.get("x", lx)
        y = settings.get("y", ly)
        if (x != UNSET_COORD): settings["x"] = x
        if (y != UNSET_COORD): settings["y"] = y

        # setup the root layout object (representing the root window)
        self.__layout_object.set_geometry(Unit.ZERO, Unit.ZERO,
                              Unit.Unit(gtk.gdk.screen_width(), Unit.UNIT_PX),
                              Unit.Unit(gtk.gdk.screen_height(), Unit.UNIT_PX))

        # build widget hierarchy
        self.new_child(childtype, settings, children)
        self.add(self.__group.get_widget())

        # run initial scripts
        for s in self.__scriptlets:
            self.execute_script(s)

        # load stored configuration
        self.__configurator.load_config()

        # unlock the geometry engine
        gobject.idle_add(self.__group.unlock_geometry)



    #
    # Sets the content of the display.
    #
    def set_content(self, childtype, settings, children):

        self.__content = (childtype, settings, children)



    #
    # Sets the callbacks for the responses (about and readme dialogs).
    #
    def __about_response_callback(self, about, response_id):
        if (response_id < 0):
            self.__about.hide()
            self.__about.emit_stop_by_name("response")
        elif (response_id == 2003):
            self.__open_readme()
        elif (response_id == gtk.RESPONSE_CLOSE):
            self.__about.hide()



    def __about_close_and_delete_callback(self, about, event=None):

        self.__about.hide()
        return True



    def __readme_response_callback(self, readme, response_id):

        if (response_id == gtk.RESPONSE_CLOSE):
            self.__readme.hide()



    def __readme_close_and_delete_callback(self, readme, event=None):

        self.__readme.hide()
        return True



    #
    # Sets metadata.
    #
    def set_metadata(self, metadata):

        pbuf = None
        fbuf = None
        rbuf = None

        preview = metadata.get("preview", "")
        name = metadata.get("name", "")
        version = metadata.get("version", "")
        copyright = metadata.get("copyright", "")
        comments = metadata.get("comments", "")
        license = metadata.get("license", "")
        website = metadata.get("website", "")
        author = metadata.get("author", "")
        category = metadata.get("category", "")
        dependency = metadata.get("dependency", "")
        description = metadata.get("description", "") + "\n"

        # a banner without the display's name would look crappy
        if (name):
            if (preview):
                preview = self.get_full_path(preview)
                data = vfs.read_entire_file(preview)
                loader = gtk.gdk.PixbufLoader()
                loader.write(data, len(data))
                loader.close()
                pbuf = loader.get_pixbuf()
            self.__configurator.set_banner(preview,
                                "<big>%s</big> %s\n"
                                "<small>%s</small>" % (name, version, author))

            # include the LICENSE file if available
            for elem in ("COPYING", "LICENSE"):
                try:
                    fbuf = open(self.get_full_path(elem), "r")
                except:
                    pass

            if (fbuf):
                license = fbuf.read()
            else:
                log("Warning: COPYING or LICENSE not included in desklet \"%s %s\".\nPlease contact the author!" % (name, version))

            # include the README file if available
            try:
                rbuf = open(self.get_full_path("README"), "r")
            except:
                log("README file not included in desklet!")

            if (rbuf):
                self.__readme_button = \
                    self.__about.add_button(_("_Readme"), 2003)
                self.__about.action_area.reorder_child(self.__readme_button,
                                                       gtk.PACK_START)
                self.__readme_buffer.set_text(rbuf.read())

            # add comments to the description
            if (comments): description = "%s\n%s\n" % (description, comments)

            # feed the About Window with the Metadata
            self.__about.set_name(name)
            self.__about.set_version(version)
            self.__about.set_copyright(copyright)
            self.__about.set_comments(description)
            if (license): self.__about.set_license(license)
            self.__about.set_website(website)
            self.__about.set_authors([author])
            self.__about.set_logo(pbuf)


    #
    # Adds the given scriptlet.
    #
    def add_scriptlet(self, code, filename):

        scriptlet = Scriptlet(code, filename)
        self.__scriptlets.append(scriptlet)



    #
    # Executes the given script.
    #
    def execute_script(self, code):

        self.__script.execute(code)



    #
    # Executes the given callback script.
    #
    def execute_callback_script(self, code, this):

        scriptlet = Scriptlet(code, self.__display_file)
        self.__script.add_element(None, "self", this)
        self.__script.execute(scriptlet)



    #
    # Adds the given target to the scripting environment.
    #
    def add_target_to_script(self, name, target):

        index_path = target.get_index_path()
        length = len(index_path)

        if ("#" in name): name = name[:name.find("#")]
        if (length > 0):
            self.__script.add_element_with_path(_ROOT, name, target, index_path)
        else:
            self.__script.add_element(_ROOT, name, target)



    #
    # Builds the configurator.
    #
    def build_configurator(self, items):

        self.__configurator.build(items)
        self.__configurator.set_path(self.__path)



    #
    # Sends an event to be executed to the display.
    #
    def send_event(self, etype, *args):

        if (not self.__is_sensitive): return
        w, h = self.__group.get_widget().size_request()
        lx, ly = self.__pointer_pos

        self.__action_stamp += 1
        actions = []

        if (etype == self.EVENT_MOTION):
            x, y = args
            utils.request_idle_call(self.__queue_motion, x, y, w, h, False)
            return

        elif (etype == self.EVENT_LEAVE):
            utils.request_idle_call(self.__queue_motion, 0, 0, w, h, True)
            return

        elif (etype == self.EVENT_PRESS):
            button, x, y, counter = args
            self.__pointer_pos = (x, y)
            if (counter == 1):
                action = DisplayTarget.ACTION_PRESS
            else:
                action = DisplayTarget.ACTION_DOUBLECLICK

            event = Struct(button = button, _args = [button])
            actions.append((action, event))

        elif (etype == self.EVENT_RELEASE):
            button, x, y = args
            if (button == 1):
                if (abs(lx - x) < 10 and abs(ly - y) < 10):
                    action = DisplayTarget.ACTION_CLICK
                    event = Struct(button = button, _args = [button])
                    actions.append((action, event))

                action = DisplayTarget.ACTION_RELEASE

            elif (button == 2):
                return
            elif (button == 3):
                action = DisplayTarget.ACTION_MENU
            else:
                return
            event = Struct(button = button, _args = [button])
            actions.append((action, event))

        elif (etype == self.EVENT_SCROLL):
            direction, x, y = args
            if (direction == gtk.gdk.SCROLL_UP):
                direction = 0
            elif (direction == gtk.gdk.SCROLL_DOWN):
                direction = 1
            else:
                direction = -1
            action = DisplayTarget.ACTION_SCROLL
            event = Struct(direction = direction, _args = [direction])
            actions.append((action, event))

        elif (etype == self.EVENT_KEY_PRESS):
            key, x, y = args
            action = DisplayTarget.ACTION_KEY_PRESS
            event = Struct(key = key)
            actions.append((action, event))

        elif (etype == self.EVENT_KEY_RELEASE):
            key, x, y = args
            action = DisplayTarget.ACTION_KEY_RELEASE
            event = Struct(key = key)
            actions.append((action, event))

        else:
            # what kind of event did we get there?
            import traceback; traceback.print_exc()

        for action, event in actions:
            self.__group.get_layout_object().send_action(
                Unit.Unit(x, Unit.UNIT_PX),
                Unit.Unit(y, Unit.UNIT_PX),
                self.__action_stamp,
                action, event)

        # extend the menu or create one if there's none
        if (action == DisplayTarget.ACTION_MENU):
            utils.request_idle_call(self.open_menu, [])



    #
    # Returns the path of the .display file.
    #
    def get_path(self):

        return self.__path



    #
    # Returns the full path of the given path which may be relative to the
    # .display file.
    #
    def get_full_path(self, path):

        # a path is absolute iff it starts with "/" or with a protocol name
        # such as "http://", otherwise it's relative
        if (path.startswith("/") or self.__IS_ABSOLUTE_PATH_RE.match(path)):
            return path
        else:
            return os.path.join(self.__path, path)



    #
    # Returns the display.
    #
    def _get_display(self):

        return self



    #
    # Creates and returns a new layout object as a child of this element's
    # layout object.
    #
    def new_layout_object(self):

        return self.__layout_object.new_child()



    def new_child(self, childtype, settings, children):

        # we don't catch the KeyError here, but in the DisplayFactory
        try:
            self.__group = targetregistry.create(childtype, self)
        except KeyError, exc:
            log("Error: %s\n" % `exc`)
        self.__group.get_widget().show()
        cid = settings["id"]
        self.add_target_to_script(cid, self.__group)

        for t, s, c in children:
            self.__group.new_child(t, s, c)

        for key, value in settings.items():
            self.__group.set_xml_prop(key, value)



    #
    # Opens the configuration dialog for this display.
    #
    def __open_configurator(self):
        assert (self.__configurator)

        configurators = [s.configurator
                         for s in self.__sensor_controls.values()]

        if (configurators):
            # support old deprecated sensor stuff
            dconf = DisplayConfigurator(configurators)

        else:
            self.__configurator.show()



    #
    # Opens the about dialog for this display.
    #
    def __open_about(self):
        assert (self.__about)

        self.__about.show()


    #
    # Opens the readme dialog for this display.
    #
    def __open_readme(self):
        assert (self.__readme)

        self.__readme.show()



    #
    # Saves this display's position.
    #
    def __save_position(self):

        x, y, nil, nil = self.__group.get_user_geometry()
        positions = DefaultStateSaver().get_key("positions", {})
        positions[self.get_id()] = (x.as_px(), y.as_px())
        DefaultStateSaver().set_key("positions", positions)



    #
    # Removes this display.
    #
    def remove_display(self):

        # save the display's position
        self.__save_position()

        self.__configurator.destroy()
        self.__about.destroy()
        self.__readme.destroy()
        self.update_observer(self.OBS_CLOSED, self.__id)
        self.drop_observers()

        self.__script.stop()
        for s in self.__sensor_controls.values():
            s.stop = True
        del self.__script

        self.__group.delete()

        del self.__sensor_controls
        del self.__mapping
        del self.__group
        del self.__configurator
        self.__about.destroy()
        del self.__about
        self.__readme.destroy()
        del self.__readme
        del self.__DISPLAY_MENU
        for m in self.__menu: m.destroy()
        del self.__menu
        self.__layout_object.destroy()
        del self.__layout_object
        del self.__readme_buffer
        del self.__readme_button
        del self.__scriptlets
        del self.__content
        del self.__action_stamp
        del self.__id
        del self.__display_file
        del self.__path
        del self.__is_sensitive
        for w in self.__swindow:
            w.destroy()
        del self.__swindow

        del self.__arrays
        del self.__last_pointer_pos
        del self.__pointer_pos
        del self.__cursor_stack

        gc.collect()
#        import objgraph,inspect, random
#        print "growth"
#        objgraph.show_growth()
#        print "common"
#        objgraph.show_most_common_types()
#        objgraph.show_chain(objgraph.find_backref_chain(random.choice(objgraph.by_type('Display')), inspect.ismodule), filename='/tmp/chain.png')
#        objgraph.show_refs(random.choice(objgraph.by_type('Display')), refcounts=True, filename='/tmp/roots.png')
#        objgraph.show_backrefs(random.choice(objgraph.by_type('Display')), refcounts=True, filename='/tmp/rootsback.png')


    #
    # Purges this display.
    #
    def purge_display(self):

        # remove the display's position
        positions = DefaultStateSaver().get_key("positions", {})
        try:
            del positions[self.get_id()]
        except KeyError:
            # position wasn't stored
            pass

        # clean up scripting environment
        self.__script.remove()

        # remove the configuration
        self.__configurator.remove_config()

        gc.collect()


    #
    # Sends the given action with an event object to the display.
    #
    def send_action(self, src, action, event):

        call = src.get_action_call(action)
        if (call):

            # analyze call to see if it's a legacy call
            # FIXME: remove eventually :)
            if (re.match("\w+:.*", call)):
                log("Deprecation: Please use new style call.",
                    is_warning = True)

                try:
                    legacy_args = event._args
                except:
                    legacy_args = []

                legacy_call = actionparser.parse(call)
                path = src.get_index_path()
                self.call_sensor(legacy_call, path, *legacy_args)

            else:
                src._setp("event", event)
                self.execute_callback_script(call, src)



    def __queue_motion(self, px, py, w, h, is_leave):

        # some window managers send a LEAVE event for mouse clicks;
        # work around this
        if (is_leave and (px, py) == self.__last_pointer_pos
            and (0 <= px <= w) and (0 <= py <= h)):
            is_leave = False

        # don't do redundant work
        if (not is_leave and (px, py) == self.__last_pointer_pos): return
        else: self.__last_pointer_pos = (px, py)

        if (not is_leave):
            ux = Unit.Unit(px, Unit.UNIT_PX)
            uy = Unit.Unit(py, Unit.UNIT_PX)
            self.__group.get_layout_object().send_action(ux, uy,
                                                         self.__action_stamp,
                                                   DisplayTarget.ACTION_MOTION,
                                                         Struct())
            self.__group.detect_leave(self.__action_stamp)
        else:
            self.__group.detect_leave(self.__action_stamp)



    #
    # Observer for the root group.
    #
    def child_observer(self, src, cmd):

        if (cmd == src.OBS_GEOMETRY):
            x, y, w, h = self.__group.get_geometry()
            ux, uy = self.__group.get_user_geometry()[:2]

            if (ux.is_unset() or uy.is_unset()):
                utils.request_idle_call(self.update_observer, self.OBS_GEOMETRY,
                                   UNSET_COORD, UNSET_COORD,
                                   w.as_px(), h.as_px())
            else:
                self.__save_position()
                utils.request_idle_call(self.update_observer, self.OBS_GEOMETRY,
                                   x.as_px(), y.as_px(),
                                   w.as_px(), h.as_px())



    #
    # Sets the anchored position of the display.
    #
    def set_position(self, x = UNSET_COORD, y = UNSET_COORD):

        if (x != y != UNSET_COORD):
            x = Unit.Unit(x, Unit.UNIT_PX)
            y = Unit.Unit(y, Unit.UNIT_PX)
            cx, cy, cw, ch = self.__group.get_geometry()

            if ((cx, cy) != (x, y)):
                ax, ay = self.__group.get_anchored_coords(x, y, cw, ch)
                dx, dy= x - ax, y - ay
                new_x = x.as_px() + dx.as_px()
                new_y = y.as_px() + dy.as_px()

                self.__group.set_xml_prop("x", str(new_x))
                self.__group.set_xml_prop("y", str(new_y))



    #
    # Sets the size of the display.
    #
    def set_size(self, width, height):

        self.__group.set_xml_prop("width", str(width))
        self.__group.set_xml_prop("height", str(height))



    #
    # Sets the configuration settings.
    # FIXME: remove eventually :)
    #
    def __set_settings(self, settings, sensor):

        for key, value in settings.get_entries():
            # get all (target, property) tuples that are watching the given
            # sensor key and notify the targets
            entries = self.__mapping.get((sensor, key), [])

            # if an array does not have enough elements, create them
            if (not entries and "[" in key):
                pos = key.find("[")
                port = key[:pos]
                path = key[pos + 1:-1].split("][")
                new_length = int(path.pop()) + 1
                if (port in self.__arrays):
                    array = self.__arrays[port]
                    array.set_prop("length", new_length)
                    entries = self.__mapping.get((sensor, key), [])

            for target, prop in entries:
                target.set_xml_prop(prop, value)



    #
    # Sets the window configuration.
    #
    def set_prop(self, key, value):

        if (key == "window-flags"):
            self.update_observer(self.OBS_FLAGS, value)

        elif (key == "desktop-borders"):
            self.update_observer(self.OBS_BORDERS, value)

        elif (key == "title"):
            self.update_observer(self.OBS_TITLE, value)

        elif (key == "icon"):
            filename = self.get_full_path(value)
            loader = gtk.gdk.PixbufLoader()
            try:
                data = vfs.read_entire_file(filename)
            except:
                return
            try:
                loader.write(data, len(data))
            except:
                log("Warning: Invalid image format.")
                return

            loader.close()
            pixbuf = loader.get_pixbuf()
            self.update_observer(self.OBS_ICON, pixbuf)

        elif (key == "shape"):
            if (value.lstrip().startswith("<")):
                from utils.DOM import DOM
                try:
                    from utils import svg
                except ImportError:
                    log("Could not import svg module!")
                    return
                w, h, = self.size_request()
                if (not w or not h): return
                root = DOM(value).get_root()
                root["width"] = `w`
                root["height"] = `h`
                img = gtk.Image()
                svg.render(img, w, h, str(root))
                pixbuf = img.get_pixbuf()

            else:
                filename = self.get_full_path(value)
                loader = gtk.gdk.PixbufLoader()
                try:
                    data = vfs.read_entire_file(filename)
                except:
                    log("Couldn't read file %s", (filename,))
                    return
                try:
                    loader.write(data, len(data))
                except:
                    log("Warning: Invalid image format.")
                    return

                loader.close()
                pixbuf = loader.get_pixbuf()

            pix, mask = pixbuf.render_pixmap_and_mask(1)
            self.update_observer(self.OBS_SHAPE, mask)



    #
    # Changes the mouse cursor.
    #
    def __set_cursor(self):

        if (self.__cursor_stack):
            cursor = self.__cursor_stack[-1]
        else:
            cursor = None

        self.update_observer(self.OBS_CURSOR, cursor)



    #
    # Adds a cursor to the cursor stack.
    #
    def push_cursor(self, cursor):

        self.__cursor_stack.append(cursor.upper())
        utils.request_call(self.__set_cursor)



    #
    # Removes a cursor from the cursor stack.
    #
    def pop_cursor(self, cursor):

        try:
            self.__cursor_stack.remove(cursor.upper())
        except:
            pass
        utils.request_call(self.__set_cursor)



    #
    # Adds a sensor to this display.
    # FIXME: remove eventually :)
    #
    def add_sensor(self, ident, sensor):

        def set_menu(menu):

            m = []
            cnt = 0
            for entry in menu[:-1]:
                if (not entry):
                    m.append(MenuItem("/sep%d" % cnt))
                else:
                    callback = entry[3]
                    args = [None] + list(entry[4])
                    m.append(MenuItem("/item%d" % cnt, entry[0], None,
                                      callback, args))
                cnt += 1

            utils.request_call(self.open_menu, m)

        self.__sensor_controls[ident] = sensor
        sensor.bind("output", self.__set_settings, ident)
        sensor.bind("menu", set_menu)



    #
    # Binds a sensor's output to an element.
    # FIXME: remove eventually :)
    #
    def bind_sensor(self, sensorplug, element, prop):

        def h(value, element, prop, port):
            for k, v in value.items():
                if (k == port):
                    element.set_xml_prop(prop, v)

        ident, port = sensorplug.split(":")
        if (not (element, prop) in
              self.__mapping.setdefault((ident, port), [])):
            self.__mapping[(ident, port)].append((element, prop))



    #
    # Calls a function of a Sensor.
    # FIXME: Remove eventually
    #
    def call_sensor(self, cmd, path, *args):
        assert(cmd)

        args = list(args)
        for ident, callname, userargs in cmd:
            sensorctrl = self.__sensor_controls[ident]

            allargs = args + userargs

            # the sensor is an external module, so we make sure it cannot crash
            # the application
            try:
                sensorctrl.action = (callname, path, allargs)

            except StandardError, exc:
                log("The sensor produced an error: %s" % (exc,))



    #
    # Unbinds a sensor's output from an element.
    # FIXME: remove eventually :)
    #
    def unbind_sensor(self, sensorplug, element, prop):

        ident, port = sensorplug.split(":")
        try:
            self.__mapping[(ident, port)].remove((element, prop))
        except KeyError:
            pass



    #
    # Registers an array to be parent array of the given child.
    # FIXME: remove eventually :)
    #
    def register_array_for_port(self, array, sensorplug):

        ident, port = sensorplug.split(":")
        self.__arrays[port] = array



    #
    # Returns the anchored geometry of this display.
    #
    def get_geometry(self):

        try:
            x, y, w, h = self.__group.get_geometry()
            ax, ay = self.__group.get_anchored_coords(x, y, w, h)
            dx, dy = x - ax, y - ay
            return (x + dx, y + dy, w, h)
        except:
            return (Unit.ZERO, Unit.ZERO, Unit.ZERO, Unit.ZERO)



    #
    # Opens a menu.
    #
    def open_menu(self, menu):

        # always work on a copy
        menu = menu[:]

        if (menu): menu.append(MenuItem("/__separator"))
        menu += self.__DISPLAY_MENU

        mainmenu = gtk.Menu()
        tree = {}
        for entry in menu:
            if (not entry.label):
                item = gtk.SeparatorMenuItem()

            elif (entry.icon):
                if (gtk.stock_lookup(entry.icon)):
                    item = gtk.ImageMenuItem(entry.icon)
                    if (entry.label):
                        item.get_children()[0].set_text_with_mnemonic(entry.label)

                else:
                    item = gtk.ImageMenuItem(entry.label)
                    try:
                        img = Tiling()
                        data = vfs.read_entire_file(self.get_full_path(entry.icon))
                        img.set_from_data(data)
                        img.render(16, 16, 1, 1)
                        img.show()
                        item.set_image(img)
                    except:
                        import traceback; traceback.print_exc()

            else:
                item = gtk.MenuItem(entry.label)

            if (entry.callback):
                item.connect("activate",
                             lambda src, cb, args: cb(*args),
                             entry.callback, entry.args)

            item.show()
            if (not entry.active): item.set_sensitive(False)

            menupath = "/".join(entry.path.split("/")[:-1])

            if (menupath):
                parentitem = tree.get(menupath)

                if (not parentitem.get_submenu()):
                    m = gtk.Menu()
                    parentitem.set_submenu(m)
                else:
                    m = parentitem.get_submenu()

            else:
                m = mainmenu

            m.append(item)
            tree["/".join(entry.path.split("/"))] = item

        mainmenu.popup(None, None, None, 0, 0)
        self.__menu.append(mainmenu)


    def __handle_configure(self, *args):

        self.__open_configurator()



    def __handle_move(self, *args):

        self.update_observer(self.OBS_GEOMETRY, UNSET_COORD, UNSET_COORD, 0, 0)



    def __handle_source(self, *args):

        from config import settings

        os.system("%s \"%s\" & disown" % (settings.editor, self.__display_file))


    def __handle_restart(self, *args):

        self.update_observer(self.OBS_RESTART, self.__id)
        gc.collect()


    def __handle_remove(self, *args):

        self.close()



    def __handle_disable(self, *args):
    
        self.update_observer(self.OBS_DISABLE, self.__id)


    def __handle_about(self, *args):

        self.__open_about()



    def close(self):

        def remove_display(*args):
            self.update_observer(self.OBS_CLOSE, self.__id)

        utils.dialog.question(_("Do you really want to remove this desklet?"),
                              _("This desklet will no longer be displayed "
                                "and its configuration will be purged."),
                              (gtk.STOCK_CANCEL, None),
                              (gtk.STOCK_DELETE, remove_display)
                             )



    #
    # Returns a unique ID string.
    #
    def make_id():
        return "id%d%d" % (int(time.time() * 100), random.randrange(0xffff))

    make_id = staticmethod(make_id)

