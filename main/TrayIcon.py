from main import ICON

import gtk


class TrayIcon:

    """ Class for a simple tray icon container. """

    def __init__(self):

        self.__traymenu = gtk.Menu()

#        self.__trayicon = gtk.status_icon_new_from_file(ICON)
#        self.__trayicon.connect("popup-menu", self.__on_button)
        self.__trayicon = gtk.StatusIcon()
        self.__trayicon.set_from_file(ICON)
        self.__trayicon.set_tooltip("gDesklets StatusIcon")
        self.__trayicon.connect("popup-menu", self.__on_button, self.__traymenu)
        self.__trayicon.set_visible(True)



    def __on_button(self, widget, button, time, data = None):

#        self.__menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.__trayicon)

        if (button == 3):
            if data:
                data.show_all()
                data.popup(None, None,  gtk.status_icon_position_menu, button, time, self.__trayicon)
                data.select_first(False)
        pass



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
            self.__traymenu.append(item)
        self.__trayicon.set_visible(True)

