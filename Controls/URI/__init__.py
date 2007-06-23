from libdesklets.controls import Control

import os

from utils import vfs

from IURI import IURI

class URI(Control, IURI):

    def __init__(self):

        self.__data = ""
        self.__fd   = None
        self.__list = []
        self.__uri  = ""

        Control.__init__(self)



    def __get_file(self):

        return self.__uri

    def __set_file(self, val):

        self.__uri = val
        try:
            self.__fd = vfs.open(self.__uri, OPEN_READ)
        except:
            raise IOError("Could not open file %s." % (self.__uri))

        self._update("uri")



    def __read_file(self):

        while (True):
            try:
                d = self.__fd.read(1024)
            except:
                break
            if (not d): break
            else: self.__data += d



    def __get_raw_content(self):

        self.__read_file()
        return self.__data



    def __get_strip_content(self):

        self.__read_file()
        self.__list.extend( self.__data.splitlines() )
        return self.__list



    def __get_splitted_content(self):

        self.__read_file()
        lines = self.__data.strip()
        self.__list = lines.split()
        return self.__list


    file  = property(__get_file, __set_file, doc="raw file content")
    raw   = property(__get_raw_content, doc="raw file content")
    stripped = property(__get_strip_content, doc="stripped file content")
    splitted = property(__get_splitted_content, doc="splitted file content")


def get_class(): return URI
