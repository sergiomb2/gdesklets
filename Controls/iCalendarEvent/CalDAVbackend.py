#TODO: Consider
# - Saving unwritten events locally when we cannot write to server
# - Download events to a local file

import re
from icalendar import Calendar, Event
from httplib import BadStatusLine
from events import *
import myProduct

WebDAVAvailable = False
importerr = ""

try:
    from urlparse import urlparse, urlunsplit
except:
    importerr = "missing urlparse, therefore, no CalDAV support!"
    #WebDAVAvailable = False
else:
    try:
        import dav
    except:
        importerr = "can't import 'dav' directory in iCalendarEvent Control's directory; no CalDAV support!"
        #WebDAVAvailable = False
    else:
        WebDAVAvailable = True

# 3 minutes
POLL_CYCLES = 18

# Eliminate all CREATED tags.  Some apps (*ahem* Google Calendar) set this
# to a weird, illegal date (00001231T000000Z).
# We have to catch it before we try to create a Calendar from it.
re_CREATED = re.compile("^CREATED.*", re.MULTILINE)

#
# CalDAV handler
#
class CalDAVbackend:
    """
    Try to create an instance of this class.  It will raise
    an ImportWarning if it could not import the proper modules.
    This tries to load a CalDAV calendar from uri.
    This will raise a LookupError if it can't fetch the resource.
    Returns an icalendar Calendar object.
    """
    def __init__(self):
    
        if not WebDAVAvailable:
            raise ImportWarning(importerr)
        
        self.__resource = None
        self.__ctag = ""
        self.__color = ""
    
    def registerChangeCallback(self, func, uri):
    
        self.__changeCallback = func
        self.__pollCntr = 0
    
    def pollForChanges(self):
    
        self.__pollCntr += 1
        
        if self.__pollCntr >= POLL_CYCLES:
        
            if self.__resource:
            
                try:
                  self.__resource.update()
                except dav.davresource.DAVError, (status, reason, davresource):
                  print "Polling calendar for changes failed (%s: %s)" % (status, reason)
                  print "Will retry next chance we get, don't worry"
                  self.__pollCntr -= 1
                  return True
                except: # BadStatusLine:
                  # Poll for changes again as soon as we can
                  self.__pollCntr -= 1
                  return True
                
                ctag = self.__resource.get_resource_property('getctag', 'http://calendarserver.org/ns/')
                if ctag and (self.__ctag != ctag):
                    self.__ctag = ctag
                    self.__changeCallback(None, FILE_CHANGED)
            
            self.__pollCntr = 0
        
        # This function will be called again forever until it's removed
        return True
    
    def refresh(self, uri):
        """
        Refreshes the resource if it exists.
        Returns True on success, False on failure.
        """
        # Update the resource if it exists
        if self.__resource:
        
            print "trying to update CalDAV calendar"
            try:
                self.__resource.update()
            except:
                # Move on to the other condition
                print "update failed, will try to fetch"
                self.__resource = None
        
        # Don't make this an 'else', we may have to handle the above exception
        if not self.__resource:
            if not self.__open(uri, ''):
                print "failed to refresh by re-fetching"
                return False
        
        # Check to see if the update failed...
        if self.__resource._result == None:
            print "Resource failed to update"
            return False
    
        return True
    
    def read(self, uri):
        """
        Returns an icalendar Calendar object no matter what.
        (If the calendar's empty, it should be an empty
        calendar...)
        """
        # Try opening it
        if not self.__open(uri, ''):
            # Do nothing but stop processing
            print "failed to open remote resource for reading"
            raise LookupError
        
        # Iterate through calendars fetched from the remote server
        # It seems CalDAV (or at least Google Calendar) adds one
        # calendar "child object" per event
        #TODO: will this raise an error?
        cal_string = ""
        try:
            for rcal in self.__resource.get_child_objects():
                cal_string += '\n' + rcal.get().read()
        except dav.davresource.DAVError, (status, reason, davresource):
            print "Reading child elements of calendar failed (%s: %s)" % (status, reason)
            raise
        # Eliminate all instances of the CREATED tag
        cal_string = re_CREATED.sub("", cal_string)
        try:
            tmp_cals = Calendar.from_string(cal_string, multiple=True)
        # If it fails to open, don't update 'events'
        except:
            print "that's odd...icalendar couldn't read fetched calendars..."
            print cal_string
            raise
        else:
            # We only really want VEVENT information from each calendar
            cal = Calendar()
            for c in tmp_cals:
                for subcomponent in c.walk('VEVENT'):
                    cal.add_component(subcomponent)
        
        # If there's a calendar color, get that too
        self.__color = self.__resource.get_resource_property('calendar-color', 'http://apple.com/ns/ical/')
        return cal

    def __open(self, uri, mode):
        """
        Returns True if successfully opened the CalDAV collection,
        False otherwise.
        """
        print "fetching CalDAV calendar"
        self.__resource = None
        # First, parse the URL
        scheme, server, path, params, query, fragment = urlparse(uri)
        
        # Get username and pass from 'server'
        try:
            i = server.rindex('@')
        except:
            # Flag this condition as "no auth"
            user = None
            pw = None
            i = -1
        else:
            # getting user name and pw string didn't raise an exception
            try:
                user_end = server[:i].index(':')
            except:
                user = server[:i]
                pw = ""
            else:
                # trying to differentiate between user name and
                # pw didn't raise an exception
                user = server[:user_end]
                pw = server[user_end+1:i]
        finally:
            server = server[i+1:]
        
        if scheme == "https":
            conn = dav.DAVSConnection(server)
        elif scheme == "http":
            conn = dav.DAVConnection(server)
        else:
            # No connection obtained
            print "Can't connect; unknown scheme (%s)" % scheme
            return False
        
        if user:
            conn.set_auth(user, pw)
        
        # Build the URL w/o user and pass
        new_url = urlunsplit((scheme, server, path, params, query))
        
        self.__resource = None
        try:
            # Error here when no connection available; it can't be
            # assumed that because it didn't throw an exception it's ok
            self.__resource = dav.DAVCollection(new_url, conn)
        except dav.davresource.DAVNoCollectionError:
            print "URL is not a WebDAV \"collection\" (%s)" % new_url;
            return False
        except TypeError:
            print "Bad username (%s) or password" % user
            return False
        
        # Initialize ctag
        self.__ctag = self.__resource.get_resource_property('getctag', 'http://calendarserver.org/ns/')
        return True

    def close(self):
        """
        Closes the connection to the CalDAV server
        """
        self.__resource = None

    def new(self, cal, uri, event):
        """
        Expects an icalendar Event
        """
        if not self.__resource:
            if not self.__open(uri, 'w'):
                print "could not open \"%s\", event not created" % uri
                return
        else:
            if not self.refresh(uri):
                print "could not refresh \"%s\", event not created" % uri
                return
        
        new_cal = Calendar()
        new_cal['prodid'] = myProduct.prodid
        new_cal['version'] = myProduct.version
        new_cal.add_component(event)
        
        # Create a new file; the name will be the pseudorandom UID
        try:
            self.__resource.create_file(event['uid'] + ".ics", new_cal.as_string())
        except dav.davresource.DAVCreationFailedError, (status, reason, url):
            print "File creation failed (%s, %s, \"%s\")" % (status, reason, url)
            # TODO: Make this more robust
            # If this fails, raise the error.  What else can I do?
            #self.__resource.create_file(event['uid'] + "-2.ics", new_cal.as_string())
        else:
            print "Remote file created"

    # Note: This assumes only one event is contained in each resource!
    def delete(self, cal, uri, uid):
    
        if not self.__resource:
            if not self.__open(uri, 'w'):
                print "could not open \"%s\", event not deleted" % uri
                return False
        else:
            if not self.refresh(uri):
                print "could not refresh \"%s\", event not deleted" % uri
                return False
        
        for child in self.__resource.get_child_objects():
        
            c = Calendar.from_string( child.get().read() )
            for ev in c.walk('VEVENT'):
            
                print "UID for calendar with event %s is %s" % (ev['summary'], ev.decoded('uid', "-1"))
                if ev.decoded('uid', -1) == uid:
                    # We need to delete by the file's name
                    #self.__resource.delete(str(uid) + ".ics")
                    path = child.url.path
                    if path[-1] == '/':
                        path = path[:-1]
                    self.__resource.delete(path.split('/')[-1])
                    # Trigger a re-read ASAP
                    self.__pollCntr = POLL_CYCLES
                    break
        
        # Maybe it succeeded...
        # At least the resource doesn't need to be re-opened
        return True
