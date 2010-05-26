#
# Module for telling the user about important stuff after transition to another
# version.
#
# ~/.gdesklets/registry/version keeps the gDesklets version
#
# If it doesn't contain our version, we might want to tell the user something.
#

from main import USERHOME, VERSION
from utils import dialog

import os


#
# Compares the current gDesklets version with the version which previously ran
# and returns True if the versions match.
#
def _check_version():

    path = os.path.join(USERHOME, "registry", "version")
    try:
        version = open(path).read()
    except Exception:
        version = "old :)"

    try:
        open(path, "w").write(VERSION)
    except Exception:
        pass

    return (VERSION == version)



if (not _check_version()):
    if (VERSION.endswith("beta")):
        msg = _("This is a unstable version of gDesklets. Unstable versions " \
                "represent the current state of development and might be " \
                "unstable or cause problems from time to time.\n\n" \
                "If you're new to gDesklets, it is thus highly recommended to "
                "<b>not</b> use this version, but a stable release!\n\n"
                "If you still want to run the unstable version instead of a "
                "stable release version, we'd highly appreciate it if you "
                "report any weird behavior to the developers.\n\n"
                "Experienced users are encouraged to try a bzr version, "
                "though!")

    elif ("rc" in VERSION):
        msg = _("This is a <b>release candidate</b> of an upcoming gDesklets "
                "release.\nPlease test it and report bugs to "
                "<i>https://bugs.launchpad.net/gdesklets</i>\n"
                "This version might break your configuration or it won't "
                "restore it from an earlier release. In most cases this is "
                "intentional, since gDesklets is still in its early stages of "
                "development.\n\nThanks for testing this release candidate!")

    else:
        # our informative transition message which we can change with
        # every release
        msg = _("This version of gDesklets features the Float mode: "
                "press a key and all your desklets will come to front, "
                "floating above your applications, until "
                "you press that key again!\n"
                "The default keybinding is &lt;Shift&gt; &lt;F12&gt;, "
                "but you can easily change that in the configuration "
                "dialog.\n\n"
                "Please note that due to limitations of older X servers, "
                "you might see blocks around desklets in Float mode. "
                "This cannot be solved in a satisfying way.")

    # show the dialog
    dialog.info(
        _("Please note (this message will appear only once):"), msg)

