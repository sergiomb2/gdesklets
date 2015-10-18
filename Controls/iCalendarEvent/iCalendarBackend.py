from icalendar import Calendar, Event
from events import *
import myProduct

try:
    from gamin import WatchMonitor
except:
    print "no gamin python bindings! no file monitoring!"
    GaminAvailable = False
else:
    GaminAvailable = True

# 15 minutes
POLL_CYCLES = 90

#
# iCalendar backend interface
#
class iCalendarBackend:

    def __init__(self):
    
        if GaminAvailable:
            self.__monitor = WatchMonitor()
        else:
            self.__monitor = None

        self.__pollCntr = 0
    
    def registerChangeCallback(self, func, uri):
        """
        The change callback function takes 2 arguments: path and event.
        If we can't use gamin, we don't even care about the path - all
        we can do is report back when it's time to re-read the file and
        pretend that the file changed (since we don't really know if it
        did or not).
        """
        if self.__monitor:
            self.__monitor.watch_file(uri, func)
        else:
            self.__changeCallback = func
    
    def pollForChanges(self):
    
        if self.__monitor:
            self.__monitor.handle_events()
        else:
            self.__pollCntr += 1
            if self.__pollCntr == POLL_CYCLES:
                self.__changeCallback(None, FILE_CHANGED)
                self.__pollCntr = 0
        
        # This function must be called again forever until it's removed
        return True
    
    def read(self, uri):
    
        return Calendar.from_string( open(uri, 'rb').read() )
    
    def new(self, cal, uri, event):
    
        if not cal:
        
            print "creating new calendar"
            cal = Calendar()
            cal['prodid'] = myProduct.prodid
            cal['version'] = myProduct.version
            
        if uri == "" or uri == None:
        
            import os
            uri = os.path.join(os.path.expanduser("~"),
                               ".gdesklets",
                               "gdesklets-calendar" + os.extsep + "ics")
            
            print "creating new file %s" % uri
        
        # Add the event to the calendar
        cal.add_component(event)
        
        try:
            tmp_cal_string = cal.as_string()
        except ValueError, error:
            print "ValueError in %s: \"%s\"\n" % (uri, error)
            print "This is a python issue, but could be solved in the icalendar package."
            print "Work around it by removing the offending dates in %s ." % uri
            return
        else:
            # I think it'd be a shame to have to re-read the file just
            # to get this event added to the list.
            # Is there a way to temporarily disable gamin monitoring while
            # the file is open?
            # TODO: investigate
            f = open(uri, 'wb')
            f.write(tmp_cal_string)
            f.close()
    
    def delete(self, cal, uri, uid):
    
        for c in cal.walk('VCALENDAR'):
        
            new_cal = Calendar()
            new_cal['prodid'] = c.decoded('prodid', myProduct.prodid)
            new_cal['version'] = c.decoded('version', myProduct.version)
            # The old calendar's properties have to be added manually
            # since the Calendar() constructor seems to generate a
            # vCalendar already.
            # That, and without the following edit of cal.walk(),
            # new_cal would've given us a calendar within a calendar
            for k in c.keys():
                new_cal.add(k, c[k])
            # First we need to find an event in self.__cal with the
            # given uid
            # But not all components are vEvents and not all vEvents
            # necessarily have 'uid' (maybe)
            for component in [n for n in c.walk() if c.name != 'VCALENDAR']:
            
                try:
                    if component.name == 'VEVENT' and component['uid'] == uid:
                        # Delete this one (in other words, don't add it)
                        print "Deleting %s" % component['summary']
                    else:
                        new_cal.add_component(component)
                except:
                    new_cal.add_component(component)
            
            # Maybe this isn't absolutely necessary
            # Maybe gamin file monitoring could be disabled during
            # this file write as well
            #TODO: investigate
            try:
                f = open(uri, 'wb')
            except:
                print "failed to open file %s" % uri
                return False
            else:
                try:
                    f.write(new_cal.as_string())
                except:
                    print "failed to write calendar or failed to convert it to a string"
                    return False
                else:
                    f.close()
        
        return True
    
    def refresh(self, uri):
        """
        Refreshes local calendar, but there's no need to before it gets re-read
        """
    
        pass

