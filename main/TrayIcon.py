from main import ICON

import gtk


class TrayIcon:

    """ Class for a simple tray icon container. """

    def __init__(self):

        self.__menu = gtk.Menu()

        self.__trayicon = gtk.status_icon_new_from_file(ICON)
        self.__trayicon.connect("popup-menu", self.__on_button)



    def __on_button(self, widget, button, time):

        if (button == 3):
            self.__menu.popup(None, None, None, button, time)


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

