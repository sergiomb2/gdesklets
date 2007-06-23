from libdesklets.controls import Control

from ICalendar import ICalendar

import calendar
import time
import datetime

class Calendar(Control, ICalendar):

    # Monday, 13th of December 2004
    __DAYS = tuple([ time.strftime('%A', datetime.date(2004, 12, 13 + d).timetuple())
                     for d in range(0, 7) ])



    __MONTHS = tuple([ time.strftime('%B', datetime.date(2004, m, 1).timetuple())
                       for m in range(1, 13) ])



    def __init__(self):
        self.__time = None
        Control.__init__(self)


    def __get_days(self):
        return self.__DAYS


    def __get_months(self):
        return self.__MONTHS


    def __set_time(self, time):

        assert 'ITime:9y703dqtfnv4w373caserz68r' in time.get_interfaces_id()
        self.__time = time


    def __ymd(self):
        return self.__time.date
    

    def __get_day(self):
        wd = calendar.weekday( *self.__ymd() )
        return self.__DAYS[ wd ]


    def __get_month(self):
        return self.__MONTHS[ self.__ymd()[1] - 1 ]



    day    = property(fget = __get_day)
    days   = property(fget = __get_days)
    month  = property(fget = __get_month)
    months = property(fget = __get_months)
    time   = property(fset = __set_time)


def get_class(): return Calendar
