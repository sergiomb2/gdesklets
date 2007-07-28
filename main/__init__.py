import os
import sys
import utils
from utils import vfs


# gDesklets home paths
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
USERHOME = os.path.join(os.path.expanduser("~"), ".gdesklets")
OLDHOME = os.path.join(HOME, os.pardir, os.pardir, "share", "gdesklets")

# we need the DISPLAY variable
try:
    DISPLAY = vfs.escape_path(os.environ["DISPLAY"].replace("/", "_"))
except KeyError:
    print "The DISPLAY variable is NOT set, which usually means, " \
          "that X isn't running!"
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
VERSION = "0.36beta"
COPYRIGHT = u"Copyright \xa9 2003 - 2007 The gDesklets Team"
DESCRIPTION = _("A desktop applet system for GNOME")
AUTHORS = ( "Martin Grimme <martin@pycage.de>",
            "Christian Meyer <chrisime@gnome-de.org>",
            "Jesse Andrews <jdandr2@cs.uky.edu>",
           u"S\xe9bastien Bacher <seb128@debian.org>",
           u"Beno\xeet Dejean <tazforever@dlfp.org>"
          )
DOCUMENTERS = ("Martin Grimme <martin@pycage.de>",
               "Joe Sapp <nixphoeni@yahoo.com>")
ICON = os.path.join(HOME, "data", "gdesklets.png")
CREDITS = (
           (_("Version %s") % (VERSION,),
           (u"Copyright \xa9 2003 - 2007", "The gDesklets Team")),

           (_("Core Programming:"),
           ("Martin Grimme", "Christian Meyer", "Jesse Andrews",
            u"Beno\xeet Dejean")),

           (_("Architecture Design:"),
           ("Martin Grimme", "Christian Meyer")),

           (_("GNOME Integration:"),
           ("Christian Neumair", "Martin Grimme", u"S\xe9bastien Bacher",
            "Christian Kellner", "Christian Meyer")),

           (_("Artwork:"),
           ("Johannes Rebhan",)),

           (_("Website:"),
           ("Marius M.M.", "Luke Stroven (previous site)",)),

           (_("Thank you:"),
           ("VidaLinux for sponsoring",
            "the http://www.gdesklets.org domain!",))
          )


def init():

    """ gDesklets init process """
    import signal
    import gtk

    # prepare GTK for threads
    try:
        gtk.gdk.threads_init()
    except AttributeError:
        gtk.threads_init()
    except Exception:
        print "No threading support available in python."
        print "Compile python with --enable-threads. Exiting!"
        sys.exit(1)

    # install signal handler to quit on Ctrl-C
    signal.signal(signal.SIGINT, gtk.main_quit)

