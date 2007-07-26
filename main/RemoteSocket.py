from main import DISPLAY, SOCKET_PATH
from main.remotecommands import *
from utils import xdr

import atexit
import os
import sys
import socket
import gobject


class RemoteSocket:
    """
      This class implements a socket server for accepting incoming commands
      from clients.
      Socket server programming not necessarily requires threads. Actually, by
      not using threads, we gain some performance and stability.
    """

    def __init__(self):

        # handlers for incoming messages
        self.__message_handlers = {}

        self.__stopevent = False

        # marks the socket as blocked, i.e. must not accept new requests
        self.__block_timeout = {}



    def start(self):
        """
          Starts the server. Call this after the handlers have been set.
        """

        import utils
        utils.makedirs(SOCKET_PATH)
        serversock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sockfile = os.path.join(SOCKET_PATH, DISPLAY)
        try:
            serversock.bind(sockfile)
        except socket.error:
            try:
                os.remove(sockfile)
            except OSError:
                log("Couldn't remove dead socket file \"%s\"." % sockfile)
                sys.exit(1)
            try:
                serversock.bind(sockfile)
            except socket.error:
                log("Couldn't bind to socket. Aborting.")
                sys.exit(1)

        serversock.listen(3)
        serversock.setblocking(False)

        atexit.register(self.__shutdown, serversock, sockfile)

        gobject.timeout_add(100, self.__server_handler, serversock, sockfile)



    def add_message_handler(self, message, handler):
        """
          Adds a new message handler.
        """

        self.__message_handlers[message] = handler



    def __shutdown(self, serversock, sockfile):
        """
          Shuts down the server and closes/removes the used socket.
        """

        self.__stopevent = True
        serversock.close()
        if (sockfile):
            os.remove(sockfile)



    def __server_handler(self, serversock, sockfile):
        """
          The socket server reactor.
        """

        if (self.__stopevent):
            return False

        try:
            cnx, addr = serversock.accept()
        except socket.error:
            pass

        else:
            # new connection
            cnx.setblocking(False)
            self.__block_timeout[cnx] = 0
            gobject.timeout_add(250, self.__client_handler, cnx)

        return True



    def __client_handler(self, clientsock):
        """
          The client server reactor. A new client gets its own new reactor.
        """

        def callback(*retval):

            self.__block_timeout[clientsock] = 0

            try:
                xdr.send(clientsock, *retval)

            # hmm, we aren't able to send somthing here
            except socket.error, exc:
                log("Socket is dead!\n%s\n" % exc)
                return False

            # the data seems to be of size zero here
            except xdr.XDRError, exc:
                log("Error: %s\n" % `exc`)

            # something really unexpected has happened
            except Exception:
                try:
                    xdr.send_error(clientsock)
                except Exception:
                    import traceback; traceback.print_exc()

        if (self.__block_timeout[clientsock] > 0):
            self.__block_timeout[clientsock] -= 1

            if (self.__block_timeout[clientsock] == 0):
                callback()
            return True

        try:
            data = xdr.recv(clientsock)

        # no data on connected socket
        except socket.error:
            return True

        # socket disconnected
        except xdr.XDRError:
            clientsock.close()
            return False

        message = data[0]
        args = data[1:]

        try:
            handler = self.__message_handlers[message]

        # message_handler doesn't exist
        except KeyError:
            log("Key %s doesn't exist in message_handlers!" % (message,))
            clientsock.close()
            return False

        # timeout after 20 * 250 ms
        self.__block_timeout[clientsock] = 20
        handler(callback, *args)
        return True

        try:
            retval = handler(*args)
            if (retval == None): retval = ()

        # something bad happened while trying to execute the handler
        except Exception:
            from utils.ErrorFormatter import ErrorFormatter
            details = ErrorFormatter().format(sys.exc_info())
            log("Execution of handler (%s, %s) failed!\n%s" % (`handler`,
                                                               `args`,
                                                               details))
            # here we get our broken pipes
            retval = ()

        try:
            xdr.send(clientsock, *retval)

        # hmm, we aren't able to send somthing here
        except socket.error, exc:
            log("Socket is dead!\n%s\n" % exc)
            return False

        # the data seems to be of size zero here
        except xdr.XDRError, exc:
            log("Error: %s\n" % `exc`)

        # something really unexpected has happened
        except Exception:
            try:
                xdr.send_error(clientsock)
            except Exception:
                import traceback; traceback.print_exc()

        return True
