#
# Client module for the gDesklets daemon. Use this module to talk to the
# daemon from external programs.
#

from main import DISPLAY, HOME, SOCKET_PATH
from main.remotecommands import *
import utils.xdr as xdr

import os
import sys
import socket
import time

from utils import i18n
import __builtin__
__builtin__._ = i18n.Translator("gdesklets")


class RemoteConnection:


    def __init__(self, path):

        self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__sock.connect(path)



    def __send(self, command, *args):

        """
        Sends the given command to the given socket and returns the answer.
        """

        xdr.send(self.__sock, command, *args)

        return xdr.recv(self.__sock)



    def open_display(self, path):

        """
        Opens a display file.

        @param path: The (VFS-)path of the display file to open.
        @type  path: str

        @return: The ID of the new display.
        @rtype : str
        """

        return self.__send(COMMAND_OPEN_DISPLAY, path)[0]



    def open_display_with_id(self, path, ident):

        """
        Opens a display file with the specified ID.

        @param path: The (VFS-)path of the display file to open.
        @type  path: str
        @param ident: The ID of the display.
        @type  ident: str
        """

        return self.__send(COMMAND_OPEN_DISPLAY_WITH_ID, path, ident)



    def open_plug(self, path):

        """
        Opens a display file as an embeddable plug.

        @param path: The (VFS-)path of the display file to open.
        @type  path: str

        @return: (id, xid) The ID of the new display and the XID of the plug
                 which is cimpliant with the XEmbed protocol.
        @rtype : str
        """

        ident, xid = self.__send(COMMAND_OPEN_PLUG, path)

        return (ident, long(xid))



    def close_display(self, ident):

        """
        Closes a display with the specified ID.

        @param ident: The ID of the display.
        @type  ident: str
        """

        self.__send(COMMAND_CLOSE_DISPLAY, ident)



    def configure(self):

        """
        Opens the configuration dialog.
        """

        self.__send(COMMAND_CONFIGURE)



    def version(self):

        """
        Shows the gDesklets version.

        @return: Tuple with the name and version of the gDesklets daemon
        @rtype : tuple(str, str)
        """

        return self.__send(COMMAND_VERSION)



    def about(self):

        """
        Shows some additional information about gDesklets.

        @return: gDesklets information
        @rtype : tuple(str, str, str)
        """

        return self.__send(COMMAND_ABOUT)



    def shutdown(self):

        """
        Shuts down the daemon.

        """

        self.__send(COMMAND_SHUTDOWN)



    def displays(self):

        """
        Shows the IDs of running displays.

        @return: The list of the IDs of the currently open displays.
        @rtype : tuple
        """

        return self.__send(COMMAND_DISPLAYS)



    def display_list(self):

        """
        Shows a list of running displays.

        @return: The list of currently open displays.
        @rtype: list
        """

        return self.__send(COMMAND_DISPLAY_LIST)



    def geometry(self, ident):

        """
        Shows the coordinates and the width, height of the display specified by
        the given ID.

        @param ident: The ID of the display.
        @type  ident: str

        @return: Tuple of the x, y, width, height.
        @rtype : tuple(int, int, int, int)
        """

        x, y, w, h = self.__send(COMMAND_GEOMETRY, ident)

        return (int(x), int(y), int(w), int(h))



    def set_remove_command(self, cmd):

        """
        Sets the remove command which will be run whenever the user removes
        a display. This can only be set once in a daemon's lifetime for
        security reasons.

        @param cmd: The command.
        @type  cmd: str
        """

        self.__send(COMMAND_SET_REMOVE_COMMAND, cmd)



def daemon_is_running(display = None):

    """
    Tells if the daemon is running.

    @param display: display on which should be queried for the daemon
    @type  display: str

    @return: True if the daemon is running, False if not.
    @rtype : bool
    """

    if (not display):
        display = DISPLAY

    path = os.path.join(SOCKET_PATH, display)

    if (os.path.exists(path)):
        try:
            connection = RemoteConnection(path)
            return (connection != None)
        except Exception:
            pass

    return False



def get_daemon(display = None):

    """ Returns the daemon. If there is no daemon running, start a new one.

    @param display: display on which should be queried for the daemon
    @type  display: str

    @return:
    @rtype :
    """

    if (not display):
        display = DISPLAY

    daemon = None
    path = os.path.join(SOCKET_PATH, display)
    boottime = time.time()

    if (daemon_is_running(display)):
        try:
            connection = RemoteConnection(path)
            daemon = connection
        except Exception:
            os.unlink(path)

    else:
        daemon_path = os.path.join(HOME, "gdesklets-daemon")
        args = " ".join([ a for a in sys.argv if a.startswith("--") ])
        os.system("%s %s &" % (daemon_path, args))

        pos = 0
        delta = 1
        for i in range(500):
            left = pos
            right = 10 - pos
            mybar = " " * left + "###" + " " * right
            sys.stdout.write("\r" + _("Connecting to daemon [%s]") % mybar)
            sys.stdout.flush()
            pos += delta
            if (pos == 0 or pos == 10):
                delta = -delta
            try:
                connection = RemoteConnection(path)
                daemon = connection
                if (daemon):
                    break
            except socket.error:
                pass
            time.sleep(0.1)

        print "\r" + " " * 40 + "\r",

        if (not daemon):
            sys.exit(_("Cannot establish connection to daemon: timeout!\n"
                        "The log file might help you solving the problem."))

    elapsed = int(1000000*(time.time() - boottime))

    if (elapsed < 1000):
        print _("Connected to daemon in %d microseconds.") % (elapsed,)
    else:
        elapsed /= 1000
        print _("Connected to daemon in %d milliseconds.") % (elapsed,)

    return daemon

