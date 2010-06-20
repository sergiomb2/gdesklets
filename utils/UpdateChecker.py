from main import VERSION_MAJOR, VERSION_MINOR, VERSION_DEV, VERSION_TYPE, VERSION
import vfs
import dialog

import gtk
from xml import sax

class _UpdateChecker(sax.handler.ContentHandler):


    # Length of time between checks, in milliseconds
    TIMEOUT = 24*60*60*1000
    UPDATE_URI = "http://gdesklets.de/update.xml"


    def __init__(self):

        self.__latest_version = {"major": VERSION_MAJOR, "minor": VERSION_MINOR, 
                                 "development": VERSION_DEV, "type": VERSION_TYPE}
        # State variables
        self.__in_update = False
        self.__update_type = "minor"
        self.__remind_again = {"major": True, "minor": True}
        # Results
        self.__new_version_available = {"major": (False, self.__latest_version), "minor": (False, self.__latest_version)}

        sax.handler.ContentHandler.__init__(self)


    def __get_update_file(self):
        """
        Returns the data in the update file if it was downloaded properly
        """
        data = None
        try:
            data = vfs.read_entire_file_urllib(self.UPDATE_URI)
        except:
            # Warning was already logged by vfs
            pass

        return data


    #
    # Searches for a version greater than the current
    # First for minors, then for the majors
    #
    def startElement(self, name, attrs):

        # Only look for <update> tags at the highest level
        if (not self.__in_update) and (name != "update"): return

        # Make sure we're okay with broken SAX parsers (see DisplayFactory)
        if name == "update" and attrs.has_key("type"):
            type = attrs["type"]

            if type == "minor" or type == "major":
                self.__in_update = True
                self.__update_type = type

        if name == "version" and attrs.has_key("major") and \
                                 attrs.has_key("minor") and \
                                 attrs.has_key("development") and \
                                 attrs.has_key("type"):
            self.__latest_version.update(attrs)


    def endElement(self, name):

        # Check the latest version at the end of the major and minor <update> tags
        if (not self.__in_update) and (name != "update"): return

        # Basic tests
        if (self.__latest_version["major"],
                self.__latest_version["minor"],
                self.__latest_version["development"]) > \
           (VERSION_MAJOR,
                VERSION_MINOR,
                VERSION_DEV):
            self.__new_version_available[self.__update_type] = (True, self.__latest_version)

        # alpha < beta < rc1 < rc2...
        elif (self.__latest_version["major"],
                self.__latest_version["minor"],
                self.__latest_version["development"]) == \
             (VERSION_MAJOR,
                VERSION_MINOR,
                VERSION_DEV):
            # Check release candidates
            if self.__latest_version["type"].startswith("rc") and VERSION_TYPE.startswith("rc"):
                if int(self.__latest_version["type"][2:]) > int(VERSION_TYPE[2:]):
                    self.__new_version_available[self.__update_type] = (True, self.__latest_version)
            # Check the other types
            if (self.__latest_version["type"] == "beta" and VERSION_TYPE in ("alpha")) or \
                    (self.__latest_version["type"].startswith("rc") and VERSION_TYPE in ("alpha", "beta")) or \
                    (self.__latest_version["type"] == "" and (VERSION_TYPE in ("alpha", "beta") or \
                                                              VERSION_TYPE.startswith("rc"))):
                self.__new_version_available[self.__update_type] = (True, self.__latest_version)


    def __format_version(self, ver):

        s = ver["major"] + "." + \
                ver["minor"] + "." + \
                ver["development"]
        if ver["type"]:
            s += "_" + ver["type"]

        return s


    def __remind(self, release_type, reminder_value):

        self.__remind_again[release_type] = reminder_value


    def check(self):
        """
        This function should be called whenever a version test is desired
        (eg. in the mainloop on a timer)
        """
        data = self.__get_update_file()
        if data:
            print data
            sax.parseString(data, self)

            for type in ["major", "minor"]:
                available, version = self.__new_version_available[type]
                if available and self.__remind_again[type]:
                    dialog.info(_("A version update is available"),
                                _("You are running version %(version)s.\n\n"
                                  "Version %(newer_version)s is available "
                                  "at %(URL)s.") %
                                      {"version": VERSION,
                                       "newer_version": self.__format_version(version),
                                       "URL": dialog.urlwrap("http://www.gdesklets.de")},
                                (_("_Stop reminding me"), lambda t=type: self.__remind(t, False)),
                                (_("_Remind me again"), None))
                    break

        # Run again next timer expiration
        return True



_singleton = _UpdateChecker()
def UpdateChecker(): return _singleton
