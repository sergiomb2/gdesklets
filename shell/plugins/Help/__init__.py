from shell.Plugin import Plugin
from TipOfTheDay import TipOfTheDay
from main import HOME, REGISTRY_PATH
from main.AboutDialog import AboutDialog

import gtk
import os


_CONFIGFILE = os.path.join(REGISTRY_PATH, "shell.config")


#
# Plugin for providing the user with help.
#
class Shell_Help(Plugin):

    def init(self):
        def obs_tip(src, cmd, value):
            if (cmd == src.OBS_TIP):
                self._set_config("current_tip", value)
            elif (cmd == src.OBS_TOGGLED):
                self._set_config("show_tip_of_the_day", value)


        current_tip = int(self._get_config("current_tip") or "0")
        if (not current_tip): current_tip = 0
        self.__tip = TipOfTheDay(current_tip)
        show_tip = (self._get_config("show_tip_of_the_day") == "True")
        self.__tip.set_show(show_tip)
        self.__tip.add_observer(obs_tip)
        self.__tip.next_tip()
        if (show_tip): self.__show_tip()

        menu = self._get_plugin("UI_Menu")
        menu.insert("Slot2", "Help")
        menu.set_item("Help", None, _("_Help"), None)
        menu.set_item("Help/Contents", gtk.STOCK_HELP, _("_Contents"), self.__show_doc)
        menu.set_item("Help/Tip", gtk.STOCK_DIALOG_INFO, _("_Tip of the Day"),
                      self.__show_tip)
        menu.set_separator("Help/Separator2")
        menu.set_item("Help/About", "gnome-stock-about", _("_About..."),
                      self.__show_about)

        self.__about = AboutDialog(os.path.join(HOME, "data"))


    def __show_doc(self):

	path = os.path.join(HOME, "doc/basic")
        os.system("yelp " + path + "/gdesklets-doc.xml&")


    def __show_tip(self):

        self.__tip.show()


    def __show_about(self):

        self.__about.show()


    def _set_config(self, key, value):

        config = self.__read_config()
        config[key] = value
        self.__write_config(config)


    def _get_config(self, key):

        config = self.__read_config()
        return config.get(key)


    def __read_config(self):

        config = {}
        try:
            data = open(_CONFIGFILE, "r").read()
        except:
            data = ""

        for l in data.splitlines():
            key, value = l.split(": ")
            config[key] = value
        return config


    def __write_config(self, config):

        out = ""
        for key, value in config.items():
            out += key + ": " + str(value) + "\n"
        try:
            open(_CONFIGFILE, "w").write(out)
        except:
            pass
        
        
def get_class(): return Shell_Help
