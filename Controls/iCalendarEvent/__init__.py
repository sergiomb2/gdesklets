from libdesklets.controls import Control

from IiCalendarEvent import IiCalendarEvent

# other python modules
from icalendar import Calendar, Event, vDatetime
# workaround for bad UIDGenerator
from string import ascii_letters, digits
import random

from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import *
from dateutil.rrule import rrule, rrulestr
from dateutil.parser import parse
from dateutil.tz import tzlocal, tzical

# for local files
from iCalendarBackend import iCalendarBackend
# for CalDAV
from CalDAVbackend import CalDAVbackend

# file-change event constants
from events import *

### Constants ###
# Period between checks of the gamin file monitor
# It kind of needs to be polled
FileChangeEventPollingPeriod = 10000 #milliseconds = 10 seconds
# In case gamin isn't installed
CalendarPollingPeriod = 1800000 #milliseconds = 30 minutes

#
# Simple event class
#
class simpleEvent:
    """Simple event class
       Contains only a few wider-used members of vEvent and
       is an iterator class
    """
    def __init__(self, uid, start_date, end_date, summary, location, attendees):
        self.uid = uid
        self.start_date = start_date
        self.end_date = end_date
        self.summary = summary
        self.location = location
        self.attendees = attendees

    def __lt__(self, other):
        return (self.start_date, self.end_date) < \
               (other.start_date, other.end_date)

#
# Control for interfacing with iCalendar files
#
class iCalendarEvent(Control, IiCalendarEvent):

    # Core
    def __init__(self):
    
        # Init
        self.__uri = ""
        # We'll use the local timezone for naive datetimes by default,
        # but if there exists a VTIMEZONE element in the iCalendar file,
        # we use that instead
        # Not sure what to use for CalDAV
        self.__tz = tzlocal # a valid tzinfo subclass
        
        self.__cal = None
        self.__all_events = []
        self.__events_this_month = []
        self.__reread_timer = -1
        
        # Setup the calendar backend
        self.__backend = iCalendarBackend
        
        # Reset the date we test against
        self.__current_date = datetime.min
        self.__current_month = datetime.now().month
        self.__current_year = datetime.now().year
        Control.__init__(self)
    
    def _shutdown(self):
        """Clean up when shutting down the Control.
           Necessary if ever this Control can be dynamically loaded and unloaded.
        """
        self.__remove_polling_timer()
    
    def __getUID(self):
        unique = ''.join([random.choice(ascii_letters + digits) for i in range(16)])
        return '%s-%s@%s' % (vDatetime(datetime.today()).ical(), unique, 'gdesklets')
    
    def __key(self, vevent):
        """Returns a key suitable for sorting on.  It's a tuple of
	   (start date, end date).
           This test is designed to give higher priority to sooner
           events.
	"""
        def vevent_as_datetime(vevent, prop, default):
            """Turns a VEVENT into a datetime object"""
            retval = vevent.decoded(prop, default)
            
            if type(retval) is date:
                retval = datetime(retval.year, retval.month, retval.day, tzinfo=tzlocal())
            elif retval.tzinfo == None:
                retval = retval.replace(tzinfo=tzlocal())
            
            return retval

	return (vevent_as_datetime(vevent, 'dtstart', datetime.min), \
		vevent_as_datetime(vevent, 'dtend', datetime.max))
    
    # Helpers
    def __remove_polling_timer(self):
        
        if self.__reread_timer >= 0:
            self._remove_timer(self.__reread_timer)
            self.__reread_timer = -1
    
    def __file_change_callback(self, path, event):
    
        if event == FILE_CHANGED or event == FILE_CREATED:
            self.__reload_events()
        elif event == FILE_MOVED:
            print "File moved...new location: %s" % path
            self.__set_uri(path)
        elif event == FILE_DELETED:
            # don't panic...maybe it'll come back
            return
    
    def __reload_events(self):
    
        #TODO: remove when done debugging
        print "-------------"
        print "reloading events"
        self.__backend.refresh(self.__uri)
        # Try reading the calendar file
        try:
            self.__cal = self.__backend.read(self.__uri)
        except:
            # Don't bother updating "events"
            print "Failed to re-read calendar \"%s\" for (%s, %s); using existing information if we have any" % (self.__uri, self.__current_year, self.__current_month)
            return
        
        if (self.__cal != None) and (self.__uri != ""):
            # Grab all events, and sort them based on end date
            self.__all_events = []
            
            min_date = datetime(self.__current_year, self.__current_month, 1, tzinfo=self.__tz())
            max_date = min_date + relativedelta(months=+1) + relativedelta(microseconds=-1)
            
            # Is there a better way to do this than creating a
            # dummy event?
            min_event = Event()
            min_event.add('dtstart', min_date)
            min_event.add('dtend', min_date)
            max_event = Event()
            max_event.add('dtstart', max_date)
            max_event.add('dtend', max_date)
            
            print "stepping through events"
            # Step through all events
            for event in self.__cal.walk('vevent'):
            
                # Filter out events not in this month
                st = event.decoded('dtstart', datetime.min)
                if (not isinstance(st, datetime)):
                    st = datetime(st.year, st.month, st.day, \
                                  0, 0, 0, 0, self.__tz())
                en = event.decoded('dtend', st + relativedelta(days=+1))
                if (not isinstance(en, datetime)):
                    en = datetime(en.year, en.month, en.day, \
                                  0, 0, 0, 0, self.__tz())

                event_length = relativedelta(en, st)

                # Non-recurring events
                if (not event.has_key('rrule') and \
                    not event.has_key('rdate') and \
                    not event.has_key('exrule') and \
                    not event.has_key('exdate')):
                
                    # Make sure this event is within this month
                    if self.__key(event) <= self.__key(min_event) >= 0 and \
                       self.__key(event) >= self.__key(max_event) <= 0:
                    
                        #print "%s - %s: %s" % (event.decoded('dtstart', " "), event.decoded('dtend'," "), event.decoded('summary', " "))
                        self.__all_events.append(event)
                    
                    
                # Recurring events
                # We have to check out each event since its start and
                # end dates don't correspond to how long the event
                # actually lasts
                else:
                
                    #TODO: how about this?
                    rule = ''
                    
                    for key in ['rrule', 'rdate', 'exrule', 'exdate']:
                    
                        if (not event.has_key(key)):
                            continue
                            
                        if (isinstance(event[key], list)):

                            for r in event[key]:
                                rule += str(r) + '\n'
                                
                        else:
                        
                            rule = str(event[key])
                    
                    r = rrulestr(rule, dtstart=st, tzinfos=self.__tz, \
                                 forceset=True)
                    events = r.between(min_date, max_date, inc=True)
                    if (not events):
                        continue
                    
                    for dt in events:
                    
                        new_event = Event()
                        try:
                            new_event.add('uid', event.decoded('uid'))
                        except:
                            pass
                        new_event.add('dtstart', dt)
                        new_event.add('dtend', dt + event_length)
                        new_event.add('summary', event.decoded('summary', ""))
                        new_event.add('location', event.decoded('location', ""))
                        new_event.add('attendees', event.decoded('attendees', ""))
                        #print "%s - %s: %s" % (dt, dt + event_length, event.decoded('summary', ""))
                        
                        self.__all_events.append(new_event)
            
            # sort the added events
            self.__all_events.sort(key=self.__key)
            
            # notify the desklet
            self._update("events")
    
    # Setters
    def __clear_latest_error(self, *args):
    
        pass
    
    def __set_uri(self, u):
    
        if u != self.__uri:
        
            # Stop the existing timer (if any)
            self.__remove_polling_timer()
            
            self.__uri = u
            
            isDAV = \
              ((u[:7] == "http://") or (u[:8] == "https://"))
            
            if isDAV:
                # This may raise an error, but if it does it indicates a larger
                # problem that the user needs to address (or not use CalDAV)
                self.__backend = CalDAVbackend()
            else:
                self.__backend = iCalendarBackend()
            
            # Setup re-read callback
            self.__backend.registerChangeCallback(self.__file_change_callback, self.__uri)
            self.__reread_timer = self._add_timer(FileChangeEventPollingPeriod, \
                                                  self.__backend.pollForChanges)
            
            # Initialize events list
            self.__reload_events()
    
    
    def __set_year_and_month(self, (y, m)):
        """Expects a month from 1 - 12 and a year more recent than 1900"""
        if self.__current_month != m or \
           self.__current_year != y:
        
            self.__current_month = m if 1 <= m <= 12 else datetime.now().month
            self.__current_year  = y if 1900 <= y else datetime.now().year
        
            self.__reload_events()
        # We shouldn't update the events list just *any* time this property is set
    
    
    def __new_event(self, new_ev):
        """Start and end strings are in the format "MM/DD/YYYY HH:MM:SS" """
        s, e, summary, location = new_ev
        
        event = Event()
        event.add('summary', summary)
        event.add('location', location)
        event.add('dtstart', datetime(int(s[6:10]), \
                                      int(s[0:2]), \
                                      int(s[3:5]), \
                                      int(s[11:13]), \
                                      int(s[14:16]), \
                                      int(s[17:19]), \
                                      0, \
                                      self.__tz()))
        event.add('dtend', datetime(int(e[6:10]), \
                                    int(e[0:2]), \
                                    int(e[3:5]), \
                                    int(e[11:13]), \
                                    int(e[14:16]), \
                                    int(e[17:19]), \
                                    0, \
                                    self.__tz()))
        event.add('dtstamp', datetime.now(self.__tz()))
        
        # Workaround for a bug in UIDGenerator
        # Wasn't fixed when this was released
        event['uid'] = self.__getUID()
        
        self.__backend.new(self.__cal, self.__uri, event)
        self.__reload_events()
    
    def __delete_event(self, uid):
    
        if self.__cal and self.__uri:
        
            self.__backend.delete(self.__cal, self.__uri, uid)
            self.__reload_events()
    
    # Getters
    def __get_uri(self):
        #TODO: return a sanitized URI (w/o password)
        return self.__uri
    
    def __get_year_and_month(self):
    
        return (self.__current_year, self.__current_month)
    
    def __get_latest_error(self):
    
        return None
    
    def __get_events_list(self):
        """A generator to return simpleEvent structures to the client"""
        for i, ev in enumerate(self.__all_events):
        
            #print "getting event %d" % (i)
            
            dt = {'dtstart':datetime.min, 'dtend':datetime.max}
            
            for key in ['dtstart', 'dtend']:
                dt[key] = ev.decoded(key, dt[key])
                
                if dt[key] != None:
                    if type(dt[key]) == date:
                        dt[key] = datetime(dt[key].year, dt[key].month, dt[key].day, tzinfo=self.__tz())
                    else: #datetime
                        if dt[key].tzinfo != None:
                            dt[key] = dt[key].astimezone(self.__tz())
                        else:
                            dt[key] = dt[key].replace(tzinfo=self.__tz())
                else:
                    # dt[key] will have it's initial value, which
                    # is a valid datetime
                    pass
            
            summary = ev.decoded('summary', "")
            location = ev.decoded('location', "")
            uid = ev.decoded('uid', str(i))
            
            attendees = ev.decoded('attendee', [])
            # force it to be a list if it's just one attendee
            if type(attendees) != list:
                attendees = [attendees]
            
            # Convert the dates from datetime types to something
            # usable by the client desklet
            (yr,mon,mday,hr,minute,sec,wkday,yday,isdst) = dt['dtstart'].timetuple()
            dtstart = {'year':yr, 'month':mon, 'day':mday, 'hour':hr, 'minute':minute, 'second':sec}
            (yr,mon,mday,hr,minute,sec,wkday,yday,isdst) = dt['dtend'].timetuple()
            dtend = {'year':yr, 'month':mon, 'day':mday, 'hour':hr, 'minute':minute, 'second':sec}
            
            yield simpleEvent(uid, dtstart, dtend, summary, location, attendees)
    
    # Properties
    uri          = property(fget = __get_uri, \
                            fset = __set_uri, \
                            doc = "URI of the active calendar. Either an absolute local path to a file or an URL in the form of http[s]://username:password@www.server.com/my/resource/ . Reading this property does not return the username and password in the URL).")

    month        = property(fget = __get_year_and_month, \
                            fset = __set_year_and_month, \
                            doc = "Refreshes (or reads) the 'events' property with events occuring within the set year (>=1900) and month (1 - 12).  Defaults to this year, this month.")

    events       = property(fget = __get_events_list, \
                            doc = "Returns a generator of simpleEvent types.  simpleEvent has 6 members (all strings): uid, start_date, end_date, summary, location, and attendees.  The dates are in the local timezone as a dict with keys 'year', 'month', 'day', 'hour', 'minute', 'second'.  attendees is a list of attendees to the event (length >= 0).")

    new_event    = property(fset = __new_event, \
                            doc = "Attempts to write an event to URI (which must've been set already).  Expects: (start_date, end_date, summary, location), strings where start_date and end_date are in the form of \"MM/DD/YYYY HH:MM:SS\".")

    delete_event = property(fset = __delete_event, \
                            doc = "Deletes event represented by its uid.")

    #error        = property(fget = __get_latest_error, \
    #                        fset = __clear_latest_error, \
    #                        doc = "Reports the latest error message, or None for no error.  Bind to it for callbacks on error; write to it to clear the latest error.")


def get_class(): return iCalendarEvent
