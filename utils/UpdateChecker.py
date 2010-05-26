import vfs
import dialog

import gtk
from xml import sax

class UpdateChecker(sax.handler.ContentHandler):


    # Length of time between checks, in milliseconds
    TIMEOUT = 60*60*1000
    UPDATE_URI = "http://gdesklets.de/update.xml"


    def __init__(self, v_maj, v_min, v_dev, v_type):

        # Version to compare against and latest version available and notified
        # This should prevent multiple notifications
        self.__version = {"major": v_maj, "minor": v_min, "development": v_dev, "type": v_type}
        self.__latest_version = {"major": v_maj, "minor": v_min, "development": v_dev, "type": v_type}
        # State variables
        self.__in_update = False
        self.__update_type = "minor"
        self.__remind_again = {"major": True, "minor": True}
        # Results
        self.__new_version_available = {"major": (False, self.__version), "minor": (False, self.__version)}

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
        if (self.__latest_version["major"] > self.__version["major"]) or \
                (self.__latest_version["minor"] > self.__version["minor"]) or \
                (self.__latest_version["development"] > self.__version["development"]):
            self.__new_version_available[self.__update_type] = (True, self.__latest_version)

        # alpha < beta < rc1 < rc2...
        elif self.__latest_version["type"] != self.__version["type"]:
            # Check release candidates
            if self.__latest_version["type"].startswith("rc") and self.__version["type"].startswith("rc"):
                if int(self.__latest_version["type"][2:]) > int(self.__version["type"][2:]):
                    self.__new_version_available[self.__update_type] = (True, self.__latest_version)
            # Check the other types
            if (self.__latest_version["type"] == "beta" and self.__version["type"] in ("alpha")) or \
                    (self.__latest_version["type"].startswith("rc") and self.__version["type"] in ("alpha", "beta")) or \
                    (self.__latest_version["type"] == "" and (self.__version["type"] in ("alpha", "beta") or \
                                                              self.__version["type"].startswith("rc"))):
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
                    dialog.info(_("A " + type + " version update is available"),
                                _("You are running version ") + self.__format_version(self.__version) +
                                    _(".\n\nVersion ") + self.__format_version(version) +
                                    _(" is available at <i>http://www.gdesklets.de</i>."),
                                (gtk.STOCK_STOP, lambda t=type: self.__remind(t, False)),
                                (gtk.STOCK_OK, None))
                    break

        # Run again next timer expiration
        return True
