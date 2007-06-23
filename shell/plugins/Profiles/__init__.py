from shell.Plugin import Plugin

import gtk


#
# Plugin for switching profiles.
#
class Shell_Profiles(Plugin):

    def init(self):
        self.__is_blocked = False
        self.__items = []
        self.__client = self._get_plugin("Core_Client")

        self.__menu = self._get_plugin("UI_Menu")
        self.__menu.insert("Slot1", "Profiles")
        self.__menu.set_item("Profiles", None, _("_Profiles"), None)
        self.__menu.set_item("Profiles/New", gtk.STOCK_NEW,
                             _("New profile..."), self.__new_profile)
        self.__menu.set_separator("Profiles/Separator")
        self.__menu.set_slot("Profiles/Slot")

        self.__build_menu()


    def __build_menu(self):

        for item, profile in self.__items:
            self.__menu.remove_item(item)

        self.__items = []
        profiles = self.__client.get_profiles()
        profiles.sort()
        profiles.reverse()
        for p in profiles:
            item = "Profiles/" + p
            self.__menu.insert("Profiles/Slot", p)
            self.__menu.set_check_item(item, p, self.__switch, p)
            self.__items.append((item, p))

        self.__set_checks()


    def __set_checks(self):

        self.__is_blocked = True

        profile = self.__client.get_profile()

        for item, p in self.__items:
            self.__menu.set_checked(item, (p == profile))

        self.__is_blocked = False


    def __switch(self, profile):

        current_profile = self.__client.get_profile()

        if (self.__is_blocked or profile == current_profile):
            self.__set_checks()
            return

        self.__client.set_profile(profile)
        self.__set_checks()


    def __new_profile(self):

        from utils.HIGDialog import HIGDialog

        dialog = HIGDialog((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OK, gtk.RESPONSE_OK),
                           gtk.STOCK_NEW, _("New profile"),
                           _("Enter the name for a new profile"))

        align = gtk.Alignment(0.0, 0.0, 1.0, 0.0)
        align.set_property("border-width", 6)
        entry = gtk.Entry()
        align.add(entry)

        def response(dialog, response):
            if (response == gtk.RESPONSE_OK):
                self.__create_profile(entry.get_text())

            dialog.destroy()

        dialog.connect("response", response)
        dialog.vbox.pack_end(align, False, False, 0)
        dialog.show_all()


    def __create_profile(self, profile):

        self.__switch(profile)
        self.__build_menu()


def get_class(): return Shell_Profiles
