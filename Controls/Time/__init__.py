from libdesklets.controls import Control

from ITime import ITime

import time
import os


#
# Control for time-related stuff.
#
class Time(Control, ITime):

    def __init__(self):

        self.__timezone = ""
        self.__timezone_offset = time.timezone

        self.__format = ""

        Control.__init__(self)

        self.__yesterday = None

        self._add_timer(1000, self.__tick_time)
        

    def __tick_time(self):

        self._update("time")
        self.__try_tick_date()
        self._update("strftime")
        return True


    def __try_tick_date(self):

        today = self.__get_date()
        
        if today != self.__yesterday:
            # all my troubles seem so far away
            self.__yesterday = today
            self._update("date")



    def __set_timezone(self, tz):

        self.__timezone = tz
        #have_tz = "TZ" in os.environ

        #old_tz = os.environ.get("TZ", "")
        #if (self.__timezone):
        #    os.environ["TZ"] = self.__timezone
        #    time.tzset()
            
        #self.__timezone_offset = time.timezone

        #if (self.__timezone):
        #    if (not have_tz): del os.environ["TZ"]
        #    else: os.environ["TZ"] = old_tz
        #    time.tzset()

        #self.__try_tick_date()
        self._update("timezone")
        #self._update("date")


    def __set_format(self, f):

        self.__format = f
        self.__get_strftime()


    def __get_timezone(self):

        return self.__timezone


    def __get_time_and_date(self):

        if (self.__timezone):
            have_tz = "TZ" in os.environ
            old_tz = os.environ.get("TZ", "")

            os.environ["TZ"] = self.__timezone
            time.tzset()

            tme = time.localtime()

            if (not have_tz): del os.environ["TZ"]
            else: os.environ["TZ"] = old_tz
            time.tzset()
        else:
            tme = time.localtime()
            
        #tme = time.gmtime(time.time() - self.__timezone_offset)            
        return tme


    def __get_time(self):

        year, month, day, hours, minutes, seconds, weekday, julian, dsflag = \
               self.__get_time_and_date()
        return (hours, minutes, seconds)


    def __get_date(self):

        year, month, day, hours, minutes, seconds, weekday, julian, dsflag = \
               self.__get_time_and_date()
        return (year, month, day)


    def __get_ticks(self):

        return time.time()


    def __get_format(self):

        return self.__format


    def __get_strftime(self):

        strftime = time.strftime(self.__format)
        return strftime



    timezone = property(__get_timezone, __set_timezone, doc = "The timezone")
    time     = property(__get_time, doc = "The current time, (h, m, s)")
    date     = property(__get_date, doc = "The current date, (y, m, d)")
    ticks    = property(__get_ticks, doc = "The current ticks in floating point numbers")
    format   = property(__get_format, __set_format, doc = "The output format for strftime")
    strftime = property(__get_strftime, doc = "strftime output")



def get_class(): return Time
