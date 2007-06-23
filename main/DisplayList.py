import os
import time

from utils import vfs


#
# Class for storing the list of profiles and their displays.
#
class DisplayList:

    __ADD = 0
    __DEL = 1

    __LOCK = "/var/lock/gdesklets.lock"

    def __init__(self, displaylist):

        # the path of the display list file
        self.__display_list = displaylist

        # the current profile
        self.__current_profile = "default"

        # table for profile -> [id]
        self.__profiles = {}

        # table for id -> path
        self.__path_table = {}

        # table for id -> profile
        self.__profiles_table = {}

        # the list of unsaved modifications to the list
        self.__modifications = []

        self.__load_list()



    #
    # Loads the display list from file.
    #
    def __load_list(self):

        self.__profiles = {}
        self.__path_table = {}
        self.__profiles_table = {}

        try:
            data = open(self.__display_list, "r").readlines()
        except IOError, exc:
            return

        try:
            self.__current_profile = data.pop(0).strip()
        except IndexError, exc:
            log("The displaylist file has wrong format, ignoring it.")
            return

        self.__profiles[self.__current_profile] = []

        for line in data:
            if (not line): continue

            try:
                ident, path, profile = line.split()
            except ValueError, exc:
                log("The displaylist file has wrong format, ignoring it.")
                return

            path = vfs.unescape_path(path)
            profile = vfs.unescape_path(profile)
            if (not profile in self.__profiles):
                self.__profiles[profile] = []
            self.__profiles[profile].append(ident)

            self.__path_table[ident] = path
            self.__profiles_table[ident] = profile



    #
    # Saves the display list to file.
    #
    def __save_list(self):

        data = [self.__current_profile + "\n"]
        for profile, idents in self.__profiles.items():
            for ident in idents:
                path = self.__path_table[ident]
                path = vfs.escape_path(path)
                profile = vfs.escape_path(profile)
                data.append("%s %s %s\n" % (ident, path, profile))

        try:
            open(self.__display_list, "w").writelines(data)
        except IOError, exc:
            log("Could not open file \"%s\" for writing data!\n%s\n"
                % (self.__display_list, exc))



    #
    # Returns whether there are unsaved modifications.
    #
    def __is_dirty(self):

        return bool(self.__modifications)



    #
    # Returns the current profile.
    #
    def get_profile(self):

        return self.__current_profile



    #
    # Sets the current profile.
    #
    def set_profile(self, profile):

        self.__current_profile = profile



    #
    # Returns a list of available profiles.
    #
    def get_profiles(self):

        if (self.__is_dirty()):
            self.commit()
        self.__load_list()

        return self.__profiles.keys()



    #
    # Returns a list of all displays in the given profile.
    #
    def get_displays(self, profile):

        if (self.__is_dirty()):
            self.commit()
        self.__load_list()

        return self.__profiles.get(profile, [])



    #
    # Looks up the data for the given display.
    #
    def lookup_display(self, ident):

        try:
            profile = self.__profiles_table[ident]
            path = self.__path_table[ident]

        except KeyError:
            raise KeyError("Could not find the path or the profile for ID "
                           "\"%s\"!" % ident)

        return (profile, path)



    #
    # Adds a new display.
    #
    def add_display(self, profile, path, ident):

        if (ident):
            self.__modifications.append((self.__ADD, profile, path, ident))



    #
    # Removes a display.
    #
    def remove_display(self, ident):

        try:
            profile, path = self.lookup_display(ident)
        except KeyError, exc:
            log("The following error occurred while removing display \"%s\"!"
                 % exc)
            return

        self.__modifications.append((self.__DEL, profile, path, ident))



    #
    # Commits all changes. You have to call this method after making changes to
    # the list.
    #
    def commit(self):

        while (os.path.exists(self.__LOCK)):
            time.sleep(0.1)

        try:
            lockf = file(self.__LOCK, "w")
            lockf.close()
        except IOError:
            pass

        profile = self.__current_profile
        self.__load_list()
        self.__current_profile = profile

        for cmd, profile, path, ident in self.__modifications:
            if (cmd == self.__ADD and not ident in self.__path_table):
                if (not profile in self.__profiles):
                    self.__profiles[profile] = []
                self.__profiles[profile].append(ident)
                self.__path_table[ident] = path
                self.__profiles_table[ident] = profile

            elif (cmd == self.__DEL):
                del self.__path_table[ident]
                del self.__profiles_table[ident]
                self.__profiles[profile].remove(ident)

        self.__modifications = []
        self.__save_list()

        try:
            os.remove(self.__LOCK)
        except OSError:
            pass
