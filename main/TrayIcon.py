from main import ICON

try:
    from utils.systray import Icon as SysTrayIcon
except ImportError:
    import sys
    log("Could not import systray module!")
    sys.exit(1)

try:
    from utils.tiling import Tiling
except ImportError:
    import sys
    log("Could not import tiling module!")
    sys.exit(1)

import gtk


class TrayIcon:

    """ Class for a simple tray icon container. """

    def __init__(self):

        icon = Tiling()
        self.__ebox = gtk.EventBox()
        self.__menu = gtk.Menu()
        self.__trayicon = SysTrayIcon("gDesklets")

        icon.set_from_file(ICON);
        icon.render(24, 24, 1, 1);

        self.__ebox.add(icon)
        self.__ebox.show_all()
        self.__trayicon.add(self.__ebox)

        self.__ebox.connect("button-press-event", self.__on_button)


    def __on_button(self, src, event):

        if (event.button == 3):
            self.__menu.popup(None, None, None, event.button, event.time)


    def set_menu(self, items):

        for entry in items:
            if (entry):
                icon, label, callback = entry
                if (icon):
                    item = gtk.ImageMenuItem(icon)
                    if (label):
                        item.get_children()[0].set_text_with_mnemonic(label)
                else:
                    item = gtk.MenuItem(label)

                if (callback):
                    item.connect("activate", callback)
            else:
                item = gtk.MenuItem()

            item.show()
            self.__menu.append(item)


    def connect(self, event, *args):

        self.__ebox.connect(event, *args)
