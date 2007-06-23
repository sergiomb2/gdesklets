from shell.Plugin import Plugin
from main import USERHOME, HOME
from main.DisplayList import DisplayList
from main import client

import os
import sys


#
# Plugin for acting as a client for the gDesklets daemon.
#
class Core_Client(Plugin):

    def init(self):
        self.__daemon = None
        self.__dsplist = DisplayList(os.path.join(USERHOME, "displays"))
        self.__get_daemon()
        profile = self.__dsplist.get_profile()
        self.set_profile(profile)


    def __get_daemon(self):

        self.__daemon = client.get_daemon()
        self.__daemon.set_remove_command(os.path.join(HOME, "gdesklets") +
                                         " _remove")


    def open_display(self, path):

        try:
            ident =  self.__daemon.open_display(path)
        except:
            self.__get_daemon()
            ident =  self.__daemon.open_display(path)

        profile = self.__dsplist.get_profile()
        self.__dsplist.add_display(profile, path, ident)
        self.__dsplist.commit()

        return ident


    def open_display_with_id(self, path, ident):

        try:
            ret = self.__daemon.open_display_with_id(path, ident)
        except:
            self.__get_daemon()
            ret = self.__daemon.open_display_with_id(path, ident)
        return ret


    def close_display(self, ident):

        try:
            self.__daemon.close_display(ident)
        except:
            self.__get_daemon()
            self.__daemon.close_display(ident)


    def get_profile(self):

        return self.__dsplist.get_profile()


    def get_profiles(self):

        return self.__dsplist.get_profiles()


    def set_profile(self, profile):

        # close displays
        current_profile = self.__dsplist.get_profile()
        displays = self.__dsplist.get_displays(current_profile)
        if (current_profile != profile):
            for ident in displays:
                try:
                    self.__daemon.close_display(ident)
                except:
                    self.__get_daemon()
                    self.__daemon.close_display(ident)
        #end if

        self.__dsplist.set_profile(profile)
        self.__dsplist.commit()

        # open displays
        displays = self.__dsplist.get_displays(profile)
        for ident in displays:
            try:
                path = self.__dsplist.lookup_display(ident)[-1]
            except KeyError, exc:
                print >> sys.stderr, exc
            try:
                self.__daemon.open_display_with_id(path, ident)
            except:
                self.__get_daemon()
                self.__daemon.open_display_with_id(path, ident)


    def get_displays(self, profile):

        displays = []
        for ident in self.__dsplist.get_displays(profile):
            try:
                profile, path = self.__dsplist.lookup_display(ident)
            except KeyError, exc:
                print >> sys.stderr, exc

            displays.append((ident, path))

        return displays


def get_class(): return Core_Client
