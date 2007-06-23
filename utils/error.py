"""
Module for handling errors and presenting them as dialogs.
"""

import __builtin__
import sys
import traceback
from ErrorFormatter import ErrorFormatter
import dialog


class UserError(StandardError):
    """
    Exception for user-visible errors.
    """
    
    def __init__(self, error, description,
                 code = None, lineno = -1, show_details = True):
        
        self.error = error
        self.description = description
        if (code): self.code = code
        if (lineno != -1): self.lineno = lineno
        self.show_details = show_details
        
        StandardError.__init__(self)



class _Error:

    def __init__(self):

        # table for mapping IDs to the .display files
        self.__ident_map = {"unknown": ""}

        # table for mapping filenames to code pieces
        self.__code_map = {}

        

    def register(self, ident, path):
        """
        Registers the given ID with the given path. This is needed so that
        the dialog can point to the broken desklet.
        """
    
        self.__ident_map[ident] = path



    def forget(self, ident):
        """
        Forgets about the given ID.
        """

        del self.__ident_map[ident]
        dialog.forget(ident)



    def register_code(self, filename, code):
        """
        Registers a piece of code with a "filename". This is needed for code
        which is not accessible as a file. The filename is a pseudo-filename,
        not a real one.
        """

        self.__code_map[filename] = code



    def __dig_down(self, tb):
        """
        Digs through the traceback looking for the place which is interesting
        for the exception, which is not necessarily where it was thrown.
        Returns a tuple (filename, lineno).
        """

        tbs = traceback.extract_tb(tb)
        filename = None
        lineno = -1
        
        found = False
        while (True and tbs):
            trace =  tbs.pop()
            filename = trace[0]
            lineno = trace[1]
            if (filename.startswith("<")):
                found = True
                break
            
        del tbs

        if (found):
            return (filename, lineno)
        else:
            return (None, -1)
    


    def handle(self, ident):
        """
        Handles the recently caught error and associates it with the given
        display ID.
        """

        exc_type, exc_value, tb = sys.exc_info()
        dspfile = self.__ident_map[ident]

        filename = None
        lineno = -1
        code = None

        # get some information from the exception
        if (hasattr(exc_value, "lineno")): lineno = exc_value.lineno
        if (hasattr(exc_value, "filename")): filename = exc_value.filename
        if (hasattr(exc_value, "code")): code = exc_value.code
        if (hasattr(exc_value, "show_details")):
            show_details = exc_value.show_details
        else:
            show_details = True


        # find the interesting piece of code
        if (not filename and lineno == -1):
            filename, lineno = self.__dig_down(tb)
        del tb

            
        if (not code): code = self.__code_map.get(filename)

        if (filename):
            if (filename.startswith("<")):
                index1 = filename.find("'")
                index2 = filename.rfind("_")
                filename = filename[index1 + 1:index2]


        # hilight bad code
        if (show_details):
            details = ErrorFormatter().format(sys.exc_info(), code, lineno,
                                              filename = filename)
        else:
            details = ""


        # present exception to the user
        if (hasattr(exc_value, "error") and hasattr(exc_value, "description")):
            log("=== " + exc_value.error + "\n" + details)
            dialog.user_error(ident,
                              exc_value.error +
                              "\n<i><small>%s</small></i>\n\n" % dspfile,
                              exc_value.description, details)
        else:
            log("=== Runtime Error\n" + details)
            dialog.user_error(ident,
                              _("Runtime Error") +
                              "\n<i><small>%s</small></i>\n\n" % dspfile,
                              _("An error occurred while executing a desklet."),
                              details)




# make UserError globally available
__builtin__.UserError = UserError

_singleton = _Error()
def Error(): return _singleton
