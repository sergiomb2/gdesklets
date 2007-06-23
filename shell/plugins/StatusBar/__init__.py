from shell.Plugin import Plugin

import gtk


class Shell_StatusBar(Plugin):

    def init(self):
        bar = gtk.Statusbar()
        bar.show()
        self.__widget = bar

        shell = self._get_plugin("UI_Shell")
        shell.set_statusbar(self.__widget)

        

    def set_status(self, text):

        self.__widget.push(self.__widget.get_context_id("message"), text)


def get_class(): return Shell_StatusBar
