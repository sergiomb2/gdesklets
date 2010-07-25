from utils import vfs

import os


class MetaData:

    """
    Class for reading and manipulating meta info of .display files.
    """

    # the valid meta keys
    KEY_AUTHOR = "author"
    KEY_NAME = "name"
    KEY_VERSION = "version"
    KEY_DESCRIPTION = "description"
    KEY_CATEGORY = "category"
    KEY_ICON = "icon"
    KEY_PREVIEW = "preview"
    KEY_WEBSITE = "website"
    KEY_LICENSE = "license"
    KEY_COPYRIGHT = "copyright"


    def __init__(self, displayfile):

        self.__file = displayfile
        self.__directory = ""
        self.__filename = ""
        self.__values = {}


        self.__directory, self.__filename = os.path.split(displayfile)
        self.__read_meta()



    def __find_meta(self, data):

        """
        Finds the meta information tag in the given data and returns a tuple of
        three strings: the part before the meta info, the meta info, and the
        part behind the meta info.
        """

        # states are: 0 find "<"
        #             1 read comment
        #             2 read meta
        state = 0

        position = 0
        limit = len(data)
        while (position < limit):
            # check every "<"
            if (state == 0):
                index = data.find("<", position)
                if (index == -1):
                    break
                position = index + 1
                if (data[index:].startswith("<!--")):
                    state = 1
                elif (data[index:].startswith("<meta")):
                    state = 2

            # ignore comments
            elif (state == 1):
                index = data.find("-->", position)
                if (index == -1):
                    break
                position = index
                state = 0

            # divide into premeta, meta, postmeta parts
            elif (state == 2):
                startpos = position + len("<meta")
                endpos = data.find(">", position)
                if (endpos == -1):
                    break
                endpos = data[:endpos].rfind("/")
                return (data[:startpos], data[startpos:endpos], data[endpos:])


        return (data, "", "")


    def  __parse_meta(self, meta):

        """
        Parses the given meta data string and returns a dictionary with keys
        and values.
        """

        # states are: 0 read key name
        #             1 read " string
        #             2 read ' string
        state = 0

        position = 0
        limit = len(meta)
        key = ""
        dikt = {}
        while (position < limit):
            # read key names
            if (state == 0):
                index = meta.find("=", position)
                if (index == -1):
                    break
                key = meta[position:index].strip()
                if (meta[index + 1].strip().startswith("\"")):
                    state = 1
                elif (meta[index + 1].strip().startswith("'")):
                    state = 2
                position = index

            # read values quoted with "
            elif (state == 1):
                position = meta.find("\"", position)
                index = meta.find("\"", position + 1)
                if (index == -1):
                    break
                value = meta[position + 1:index]
                dikt[key] = value
                position = index + 1
                state = 0

            # read values quoted with '
            elif (state == 2):
                position = meta.find("'", position)
                index = meta.find("'", position + 1)
                if (index == -1):
                    break
                value = meta[position + 1:index]
                dikt[key] = value
                position = index + 1
                state = 0


        return dikt



    def __read_meta(self):

        """ Reads the meta information in the file.  """

        data = vfs.read_entire_file(self.__file) #open(self.__file).read()

        meta = self.__find_meta(data)[1]
        if (meta):
            self.__values = self.__parse_meta(meta)

        if self.KEY_NAME not in self.__values:
            self.__values[self.KEY_NAME] = \
              os.path.splitext(os.path.basename(self.__file))[0]



    def get_directory(self):

        """ Returns the directory of the display. """
        return self.__directory



    def get_filename(self):

        """ Returns the filename of the display. """

        return self.__filename



    def get(self, key):

        """ Returns the value of the given meta key. """

        return self.__values.get(key, "")



    def __cmp__(self, other):

        """
        Compares two MetaData objects and makes MetaData objects thus sortable.
        """

        return cmp(self.get(self.KEY_NAME), other.get(other.KEY_NAME))
