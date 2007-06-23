from Observable import Observable
import wallpaper

import gobject
import time


#
# Class for reporting when the wallpaper image has changed.
#
class BGWatcher(Observable):

    OBS_CHANGE_BG = 0

    def __init__(self):

        self.__old_bg = 0
        self.__last_update = 0.0

        gobject.timeout_add(50, self.__check_bg)



    def __check_bg(self):

        try:
            ident = wallpaper.get_wallpaper_id()
            if (ident != self.__old_bg):
                self.__last_update = time.time()
                gobject.timeout_add(500, self.__notify_update,
                                    self.__last_update)
            self.__old_bg = ident

        except StandardError:
            if (self.__old_bg):
                self.__last_update = time.time()
                gobject.timeout_add(500, self.__notify_update,
                                    self.__last_update)
                self.__old_bg = 0

        return True



    def __notify_update(self, timestamp):

        if (timestamp != self.__last_update): return True
        self.update_observer(self.OBS_CHANGE_BG)

        return False

