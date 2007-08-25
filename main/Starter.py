from config import settings
from config.DaemonConfigger import DaemonConfigger
from display.Display import Display
from display.Window import Window
from display.Plug import Plug
from factory.DisplayFactory import DisplayFactory
from main import COPYRIGHT, HOME, NAME, USERHOME, VERSION
from main.AboutDialog import AboutDialog
from main.remotecommands import *
from main.RemoteSocket import RemoteSocket
from utils.KeyBinding import KeyBinding
from utils import dialog
from utils import vfs
from utils.error import Error

import gobject
import gtk
import os
import sys


# This class starts, restarts and kills Displays
class Starter:

    __DISPLAY_TYPE_WINDOW = "window"
    __DISPLAY_TYPE_PLUG = "plug"


    def __init__(self):

        # feedback dialog
        self.__feedback = LoadingFeedback()

        # the communication socket
        self.__socket = RemoteSocket()

        # the factory which reads the display's XML
        self.__factory = DisplayFactory()

        # the About dialog
        self.__about_dialog = AboutDialog(os.path.join(HOME, "data"))

        # the configuration dialog
        self.__configger = DaemonConfigger()
        self.__configger.set_close_callback(self.__on_finish_config)

        # the command which gets called when the user removes a display
        self.__remove_command = ""

        # the set of open displays as a hashtable "id -> display"
        self.__open_displays = {}
        # the paths of the display files "id -> path"
        self.__display_paths = {}

        # float mode
        self.__float_mode = False
        self.__containers = []

        # keybinder
        self.__prev_key = (0, 0)
        self.__keyb = KeyBinding()

        # set the message handlers for the socket
        self.__socket.add_message_handler(COMMAND_OPEN_DISPLAY,
                                          self.__handle_open_display)
        self.__socket.add_message_handler(COMMAND_OPEN_DISPLAY_WITH_ID,
                                          self.__handle_open_display_with_id)
        self.__socket.add_message_handler(COMMAND_OPEN_PLUG,
                                          self.__handle_open_plug)
        self.__socket.add_message_handler(COMMAND_CLOSE_DISPLAY,
                                          self.__handle_close_display)
        self.__socket.add_message_handler(COMMAND_SHUTDOWN,
                                          self.__handle_shutdown)
        self.__socket.add_message_handler(COMMAND_DISPLAYS,
                                          self.__handle_displays)
        self.__socket.add_message_handler(COMMAND_DISPLAY_LIST,
                                          self.__handle_display_list)
        self.__socket.add_message_handler(COMMAND_GEOMETRY,
                                          self.__handle_geometry)
        self.__socket.add_message_handler(COMMAND_VERSION,
                                          self.__handle_version)
        self.__socket.add_message_handler(COMMAND_ABOUT,
                                          self.__handle_about)
        self.__socket.add_message_handler(COMMAND_CONFIGURE,
                                          self.__handle_configger)
        self.__socket.add_message_handler(COMMAND_SET_REMOVE_COMMAND,
                                          self.__handle_set_remove_command)


        # socket ready, start handling requests
        self.__socket.start()

        # bind key
        key, mod = settings.float_key
        self.__keyb.bind_key(key, mod, self.__on_toggle_float_mode)
        self.__prev_key = (key, mod)

        # setup a nice systray icon
        if (settings.show_tray_icon):
            from main.TrayIcon import TrayIcon
            trayicon = TrayIcon()
            trayicon.set_menu([(None, _("_Manage desklets"),
                                self.__handle_manage),
                               (),
                               (gtk.STOCK_PROPERTIES, _("_Configuration"),
                                 self.__handle_configger),
                               (None, _("_View log"),
                                self.__handle_show_log),
                                (),
                               (None, _("_About..."),
                                self.__handle_about_dialog),
                               (),
                               (gtk.STOCK_QUIT, _("_Stop daemon"),
                                self.__handle_shutdown)])



    def __on_toggle_float_mode(self):

        # this is such a hack but works well until we introduce major changes
        # in the 0.36 release and implement it in a clean way
        self.__float_mode = not self.__float_mode
        for c in self.__containers:
            try:
                c.set_float_mode(self.__float_mode)
            except Exception:
                pass



    #
    # Reacts on observer messages from the display.
    #
    def __on_display_action(self, src, cmd, *args):

        if (cmd == src.OBS_CLOSE):
            ident = args[0]
            self.__close_display(ident)
            del src

        elif (cmd == src.OBS_RESTART):
            ident = args[0]
            path = self.__display_paths[ident]
            self.__remove_display(ident)
            def f(*args): pass
            gobject.timeout_add(250, self.__handle_open_display_with_id,
                                f, path, ident)
            del src



    #
    # Reacts on closing the configuration dialog.
    #
    def __on_finish_config(self):

        # bind key
        pkey, pmod = self.__prev_key
        key, mod = settings.float_key
        self.__keyb.unbind_key(pkey, pmod)
        self.__keyb.bind_key(key, mod, self.__on_toggle_float_mode)
        self.__prev_key = (key, mod)



    #
    # Adds the given display.
    #
    def __add_display(self, ident, path, displaytype):

        dsp = None
        container = None

        # can this happen?
        if (ident in self.__open_displays):
            return None

        Error().register(ident, path)

        # create display
        try:
            dsp = self.__create_display(ident, path)
        except Exception:
            Error().handle(ident)
            #log("Warning: Couldn't add desklet \"%s\".\n%s"  % (path, exc))
            self.__close_display(ident)
            return None

        self.__open_displays[ident] = dsp
        self.__display_paths[ident] = path

        log("Adding \"%s\" with ID \"%s\" to the desklet list."
            % (path, ident))
        dsp.add_observer(self.__on_display_action)

        # create container widget
        if (displaytype == self.__DISPLAY_TYPE_WINDOW):
            container = Window(dsp)

        # initialize display
        try:
            dsp.initialize()
        except Exception:
            Error().handle(ident)
            self.__close_display(ident)
            return None

        self.__containers.append(container)
        container.set_float_mode(self.__float_mode)
        return container



    #
    # Creates and returns a new display from the given data.
    #
    def __create_display(self, ident, path):

        try:
            data = vfs.read_entire_file(path)

        except Exception:
            log("Could not open desklet file \"%s\"." % (path,))
            raise UserError(_("Could not open desklet file \"%s\"") % (path,),
                           _("The desklet file could not be opened because "
                             "the file was not readable."),
                            show_details = False)

        display = self.__factory.create_display(ident, data, path)

        return display



    #
    # Removes the given display.
    #
    def __remove_display(self, ident):

        try:
            display = self.__open_displays[ident]
        except KeyError, exc:
            log("Warning: Couldn't remove desklet with ID \"%s\".\n%s" \
                % (ident, exc))
            return

        log("Removing \"%s\" with ID \"%s\" from the desklet list."
            % (self.__display_paths[ident], ident))
        display.remove_display()
        Error().forget(ident)

        try:
            del self.__open_displays[ident]
            del self.__display_paths[ident]
        except StandardError:
            pass

        import gc
        gc.collect()



    #
    # Closes the given display.
    #
    def __close_display(self, ident):

        if (ident in self.__open_displays):
            display = self.__open_displays[ident]
            display.purge_display()

        self.__remove_display(ident)
        if (self.__remove_command):
            os.system("%s %s &" % (self.__remove_command, ident))



    def __handle_open_display(self, callback, path):

        ident = Display.make_id()
        self.__handle_open_display_with_id(callback, path, ident)



    def __handle_open_display_with_id(self, callback, path, ident):

        if (settings.show_load_splash):
            self.__feedback.set_loading(path)

        def open_window():
            if (settings.show_load_splash):
                self.__feedback.show()

        def close_window(*args):
            if (settings.show_load_splash):
                self.__feedback.hide()

        def f(*args):
            return (ident, path, self.__DISPLAY_TYPE_WINDOW)

        def g(*args):
            return ident

        self.__pipeline([open_window, f, self.__add_display, close_window,
                         g, callback])



    def __handle_open_plug(self, callback, path):

        import time
        ident = str(time.time())
        plug = self.__add_display(ident, path, self.__DISPLAY_TYPE_PLUG)
        xid = plug.get_xembed_id()

        callback(ident, xid)



    def __handle_close_display(self, callback, ident):

        self.__remove_display(ident)
        callback()



    def __handle_version(self, callback):

        callback(NAME, VERSION)



    def __handle_about(self, callback):

        callback("%s %s" % (NAME, VERSION),
                 "%s" % (COPYRIGHT.replace(u"\xa9", u"(C)"),),
                 "This software is licensed under the terms of the GNU GPL.")



    def __handle_shutdown(self, callback, *args):

        for ident, display in self.__open_displays.items():
            try:
                display.remove_display()
            # what kind of exception are we expecting here?
            except Exception:
               log("Could not remove desklet \"%s\"!" % (display,))
        try:
            callback()
        except Exception:
            pass
        gtk.main_quit()



    def __handle_manage(self, *args):

        cmd = os.path.join(HOME, "gdesklets-shell")
        os.system(cmd + " &")



    def __handle_configger(self, *args):

        self.__configger.show()



    def __handle_about_dialog(self, *args):

        self.__about_dialog.show()



    def __handle_show_log(self, *args):

        cmd = os.path.join(HOME, "gdesklets-logview")
        os.system(cmd + " &")



    def __handle_displays(self, callback):

        callback(self.__open_displays.keys())



    def __handle_display_list(self, callback):

        callback(*self.__open_displays.values())



    def __handle_geometry(self, callback, ident):

        display = self.__open_displays[ident]

        callback(*display.get_geometry())



    def __handle_set_remove_command(self, callback, command):

        # only allow setting the remove command once for security reasons
        if (not self.__remove_command):
            self.__remove_command = command

        callback()



    #
    # Executes the given commands in a pipeline. A command takes the return
    # values of the previous command as its arguments.
    #
    def __pipeline(self, line, *args):

        next = line.pop(0)
        try:
            retval = next(*args)
        except Exception:
            from utils.ErrorFormatter import ErrorFormatter
            log(ErrorFormatter().format(sys.exc_info()))
            retval = ()

        if (line):
            if (not type(retval) in (type(()), type([]))):
                retval = (retval,)
            gobject.idle_add(self.__pipeline, line, *retval)




#
# Class for giving feedback while loading a display.
#
# TODO: move into its own file
#
class LoadingFeedback(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_CENTER)

        frm = gtk.Frame()
        frm.set_shadow_type(gtk.SHADOW_OUT)
        frm.show()
        self.add(frm)

        box = gtk.HBox(spacing = 12)
        box.set_border_width(12)
        box.show()
        frm.add(box)

        self.__icon = gtk.Image()
        box.pack_start(self.__icon)

        self.__label = gtk.Label("")
        self.__label.show()
        box.pack_end(self.__label)



    def set_loading(self, path):

        from MetaData import MetaData
        try:
            meta = MetaData(path)
            preview = meta.get(meta.KEY_PREVIEW)
        except Exception:
            preview = ""

        dirname = os.path.dirname(path)
        icon = os.path.join(dirname, preview)

        self.__label.set_markup("<big><b>Loading:</b>\n%s</big>" % path)

        self.__icon.hide()
        if (preview):
            try:
                # for him who loves small try blocks: you don't gain anything
                # from splitting up this block except for badly readable code ;)
                from utils import vfs
                data = vfs.read_entire_file(icon)
                loader = gtk.gdk.PixbufLoader()
                loader.write(data, len(data))
                loader.close()
                pbuf = loader.get_pixbuf()

                # scale icon down while preserving aspect ratio
                width = pbuf.get_width()
                height = pbuf.get_height()
                scale = 48 / float(height)
                width *= scale
                if (width > 96): width = 96

                if (abs(scale - 1.0) > 0.001):
                    pbuf = pbuf.scale_simple(int(width), 48, 3)

                self.__icon.set_from_pixbuf(pbuf)
                self.__icon.show()

            except Exception:
                pass

        #end if

        self.resize(10, 10)
        self.set_size_request(-1, -1)
