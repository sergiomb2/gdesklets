import os
import sys
import utils
import gtk
from utils import vfs


# gDesklets home paths
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
USERHOME = os.path.join(os.path.expanduser("~"), ".gdesklets")
OLDHOME = os.path.join(HOME, os.pardir, os.pardir, "share", "gdesklets")

# we need the DISPLAY variable
try:
    # Use gtk's get_name() to return a string containing the screen number (in
    # case the DISPLAY variable doesn't contain the screen number)
    DISPLAY = vfs.escape_path(gtk.gdk.Display(os.environ["DISPLAY"]).get_name()).replace("/", "_")
except:
    print "Error: could not open display", os.environ["DISPLAY"]
    sys.exit(1)


# the name of the purge key
PURGE_KEY = "_paths_to_purge_"

# for unset coordinates
UNSET_COORD = -1000

# paths where the display files are located
DISPLAYPATHS = (os.path.join(USERHOME, "Displays"),
                os.path.join(HOME, "Displays"),
                os.path.join(OLDHOME, "Displays"))
# paths where gDesklets looks for sensors and displays
SENSORPATHS = (os.path.join(USERHOME, "Sensors"),
               os.path.join(HOME, "Sensors"),
               os.path.join(OLDHOME, "Sensors"))
# paths where gDesklets looks for controls
CONTROLPATHS = (os.path.join(USERHOME, "Controls"),
                os.path.join(HOME, "Controls"),
                os.path.join(OLDHOME, "Controls"))
# path to the log file(s)
LOG_PATH = os.path.join(USERHOME, "logs")
# log file
LOGFILE = os.path.join(LOG_PATH, "gdesklets" + DISPLAY + ".log")
# path for registry files
REGISTRY_PATH = os.path.join(USERHOME, "registry")
# path of the communication sockets
SOCKET_PATH = os.path.join(USERHOME, "sockets")
# path containing gDesklets' PID file
PID_PATH = os.path.join(USERHOME, "gdesklets%s.pid" % DISPLAY)

# setup i18n
from utils.i18n import Translator
_ = Translator("gdesklets")


NAME = "gDesklets"
VERSION_MAJOR = "0"
VERSION_MINOR = "36"
VERSION_DEV   = "3"
VERSION_TYPE  = "beta"
VERSION = VERSION_MAJOR + "." + VERSION_MINOR + "." + VERSION_DEV
if (VERSION_TYPE): VERSION += "_" + VERSION_TYPE
COPYRIGHT = u"Copyright \xa9 2003 - 2010 The gDesklets Team"
DESCRIPTION = _("A desktop applet system for GNOME")
AUTHORS = ( "Martin Grimme <martin@pycage.de>",
            "Christian Meyer <chrisime@gnome-de.org>",
            "Jesse Andrews <jdandr2@cs.uky.edu>",
           u"S\xe9bastien Bacher <seb128@debian.org>",
           u"Beno\xeet Dejean <tazforever@dlfp.org>"
          )
DOCUMENTERS = ("Martin Grimme <martin@pycage.de>",
               "Joe Sapp <nixphoeni@yahoo.com>",
               u"Bj\xf6rn Koch <H.Humpel@gmx.de>",
               u"Robert Pastierovi\u010d <pastierovic@gmail.com>",)
ICON = os.path.join(HOME, "data", "gdesklets.png")
CREDITS = (
           (_("Version %s") % (VERSION,),
           (u"Copyright \xa9 2003 - 2010", "The gDesklets Team")),

           (_("Core Programming:"),
           ("Martin Grimme", "Christian Meyer", "Jesse Andrews", u"Beno\xeet Dejean",)),

           (_("Additional Programming:"),
           (u"Mario Gonz\u00e1lez", "Lauri Kainulainen", u"Bj\xf6rn Koch", u"Robert Pastierovi\u010d",)),

           (_("Architecture Design:"),
           ("Martin Grimme", "Christian Meyer",)),

           (_("GNOME Integration:"),
           ("Christian Neumair", "Martin Grimme", u"S\xe9bastien Bacher", "Christian Kellner", "Christian Meyer")),

           (_("Documentation:"), 	
           ("Martin Grimme", "Joe Sapp", u"Bj\xf6rn Koch", u"Robert Pastierovi\u010d",)),

           (_("Artwork:"),
           ("Johannes Rebhan",)),

           (_("Website:"),
           ("Lauri Kainulainen", "Marius M.M. (previous site)", "Luke Stroven (previous site)",)),

           (_("Thank you:"),
           ("VidaLinux for sponsoring",
            "the http://www.gdesklets.org domain!",
            "LinuxProfessionals for sponsoring",
            "webspace and the",
            "http://www.gdesklets.de domain!",)
           )
          )

