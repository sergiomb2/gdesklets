from StateSaver import DefaultStateSaver
from ConfigDialog import ConfigDialog
from main import ICON, VERSION
from utils.datatypes import *
import settings

import getopt
import sys


class DaemonConfigger(ConfigDialog):
    """
      Configuration Dialog for the daemon.
    """

    __ITEMS = (
      ("title", {"label": _("Editor to view/edit the desklet source code")}),
      ("uri",   {"label": _("Your favorite editor"),
                 "bind": "editor"}),
      ("title", {"label": _("XComposite support (requires composition manager)" +
                            "\n     <small><i>" +
                            _("this does not work with GTK 2.8 or higher for "
                              "technical reasons") + "</i></small>")}),
      ("boolean", {"label": _("Translucency (takes effect after restarting a display)"),
                   "bind": "translucency"}),
      ("title", {"label": _("Screen Resolution (DPI)")}),
      ("dpi",   {"label": "<small>" +
                          _("Adjust the value above so that the bar will be "
                            "exactly <b>5 cm</b> or <b>1.97\"</b> wide") +
                          "</small>",
                          "bind": "dpi", "value": 96}),
      ("title", {"label": _("Behavior")}),
      ("boolean", {"label": _("Show _tray icon (takes effect after restart)"),
                              "bind": "trayicon"}),
      ("boolean", {"label": _("Show _notification while loading a desklet"),
                              "bind": "loadsplash"}),
      ("keybinding", {"label": _("Key for toggling Float mode:"),
                      "bind": "float_key"})

      )


    def __init__(self):

        self.__backend = DefaultStateSaver()

        ConfigDialog.__init__(self)

        self.set_property("title", _("Configuration"))
        self.set_banner(ICON, "<big>gDesklets Configuration</big>\n"
                        "Version %s" % (VERSION,))

        self._set_setter(self.__setter)
        self._set_getter(self.__getter)
        self._set_caller(self.__caller)

        self.build(self.__ITEMS)

        self.__load_config()
        self.__read_cmd_line()



    def __setter(self, key, value, datatype):

        if (key == "editor"):
            settings.editor = value

        elif (key == "dpi"):
            settings.dpi = value

        elif (key == "float_key"):
            settings.float_key = value

        elif (key == "translucency"):
            settings.translucent = value

        elif (key == "loadsplash"):
            settings.show_load_splash = value

        elif (key == "trayicon"):
            settings.show_tray_icon = value

        self.__backend.set_key(key, value)


    def __getter(self, key):

        if (key == "editor"):
            return settings.editor

        elif (key == "dpi"):
            return settings.dpi

        elif (key == "float_key"):
            return settings.float_key

        elif (key == "translucency"):
            return settings.translucent

        elif (key == "loadsplash"):
            return settings.show_load_splash

        elif (key == "trayicon"):
            return settings.show_tray_icon

        else:
            return "gDesklets killed a kitten!"


    def __caller(self, *args): pass


    def __load_config(self):

        settings.editor = self.__backend.get_key("editor", settings.editor)
        settings.dpi = self.__backend.get_key("dpi", settings.dpi)
        settings.float_key = self.__backend.get_key("float_key",
                                                    settings.float_key)
        settings.translucent = self.__backend.get_key("translucency",
                                                      settings.translucent)
        settings.show_load_splash = self.__backend.get_key("loadsplash",
                                                     settings.show_load_splash)
        settings.show_tray_icon = self.__backend.get_key("trayicon",
                                                       settings.show_tray_icon)

    def __read_cmd_line(self):

        OPTIONS = ("sm-client-id=", "sm-config-prefix=", "sm-disable",
                   "no-tray-icon", "translucent")

        #
        # Parses the given list of command line arguments. This is usually
        # sys.argv[1:].
        #

        try:
            opts, rest = getopt.getopt(sys.argv[1:], "nop:v", OPTIONS)
        except getopt.GetoptError:
            return

        for o, a in opts:
            if (o == "--translucent"):
                settings.translucent = True
            elif (o == "--no-tray-icon"):
                settings.show_tray_icon = False
            elif (o in ("--sm-client-id", "--sm-config-prefix",
                        "--sm-disable")):
                pass
        #end for
