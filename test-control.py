#!/usr/bin/python2
# A simple script to test controls interactively.

from plugin.Interface import Interface
from main import HOME
from plugin import Permission


import sys
import os
# Interactive shell
try:
    from IPython.Shell import IPShellEmbed
    def InteractiveConsole(banner):
        (IPShellEmbed('', banner=banner))()
except:
    import code
    InteractiveConsole = code.InteractiveConsole().interact
import __builtin__

# DBus
try:
    from dbus.mainloop.glib import DBusGMainLoop
except:
    pass
else:
    DBusGMainLoop(set_as_default=True)

if "." not in sys.path: sys.path.append(".")
if HOME not in sys.path: sys.path.append(HOME)

try:
    path = os.path.abspath(sys.argv[1])
    folder, base = os.path.split(path)
except:
    sys.exit("Usage: test-control.py <control-directory>")


cwd = os.getcwd()
os.chdir(folder)
try:
    module = __import__(base)
    os.chdir(base)
    clss = module.get_class()
    ctrl = clss()

except IOError:
    sys.exit("Could not load control %s." % (path))

print
print Interface.text_describe(clss)

__builtin__.ctrl = ctrl
InteractiveConsole("Use 'ctrl' to access the control. "
                   "Press Ctrl+D to quit.")
