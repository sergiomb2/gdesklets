from libdesklets.controls import Control
from IArrayBuffer import IArrayBuffer


#----------------------------------------------------------------------------------#
#
# ArrayBuffer Class
#
#
class ArrayBuffer(Control, IArrayBuffer):

        #
        # ArrayBuffer Constructor
        #
        def __init__(self):

                self.__buffer           = []
                self.__size             = 0
                self.__cursor           = 0
                self.__window_pos       = 0
                self.__window_size      = 0
                self.__filltype         = None

                Control.__init__(self)


        #
        # Get the current object at cursor position
        #
        def __read(self):

                return self.__buffer[self.__window_pos:self.__window_pos + \
                                     self.__window_size]


        #
        # Get the entire buffer
        #
        def __read_all(self):

                return self.__buffer


        #
        # Deletes a single line from the buffer
        #
        def __delete(self, pos):

                self.__buffer = [self.__filltype] + self.__buffer[:pos] + \
                                 self.__buffer[pos + 1:]


        #
        # Fill the buffer with an object
        #
        def __fill(self, obj):

                for i in range(self.__size):
                        self.__buffer[i] = obj


        #
        # Write object to current cursor position within buffer
        #
        def __write(self, objArr):

                n = len(objArr)

                if self.__cursor + n > self.__size:
                        if n >= self.__size:
                                tmp = n - self.__size
                                self.__buffer = objArr[tmp:]

                        else:
                                tmp = self.__size - n
                                self.__buffer = self.__buffer[self.__cursor - \
                                                              tmp:self.__cursor]
                                self.__buffer += objArr

                        self.__cursor = self.__size

                else:
                        self.__buffer[self.__cursor:] = objArr + \
                                                        self.__buffer[self.__cursor + n:]
                        self.__cursor += n


        #
        # Get the current viewable window position
        #
        def __get_window_pos(self):

                return self.__window_pos


        #
        # Get the filltype
        #
        def __get_filltype(self):

                return self.__filltype


        #
        # Sets the filltype used when resizing the buffer
        #
        def __set_filltype(self, obj):

                self.__filltype = obj


        #
        # Set the viewable window position
        #
        def __set_window_pos(self, pos):

                if pos < 0:
                        pos = 0

                if pos + self.__window_size > self.__size:
                        pos = self.__size - self.__window_size

                self.__window_pos = pos


        #
        # Get the size of the viewable window
        #
        def __get_window_size(self):

                return self.__window_size


        #
        # Set the size of the viewable window
        #
        def __set_window_size(self, size):

                if size > self.__size:
                        size = self.__size

                self.__window_size = size


        #
        # Get the size of the buffer
        #
        def __get_size(self):

                return self.__size


        #
        # Set the size of the buffer
        #
        def __set_size(self, size):

                if size > self.__size:

                        tmp = [ self.__filltype for i in range(size - self.__size) ]

                        self.__buffer = tmp + self.__buffer

                else:
                        self.__buffer = self.__buffer[self.__size - size:]

                self.__size = size


        #
        # Get the current buffer cursor position
        #
        def __get_cursor(self):

                return self.__cursor


        #
        # Set the position of the buffer cursor
        #
        def __set_cursor(self, pos):

                if pos < 0:
                        pos = 0

                if pos > self.__size:
                        pos = self.__size

                self.__cursor = pos


        #
        # Interface
        #
        read        = property(fget = __read,
                               doc = "Return the viewable window array")
        read_all    = property(fget = __read_all,
                               doc = "Return the entire buffer array")
        delete      = property(fset = __delete,
                               doc = "Delete line from buffer")
        write       = property(fset = __write,
                               doc = "Write line at position cursor")
        fill        = property(fset = __fill,
                               doc = "Fill the buffer with an object")
        filltype    = property(fget = __get_filltype, fset = __set_filltype,
                               doc = "Get/Set the empty space fill type")
        window_pos  = property(fget = __get_window_pos, fset = __set_window_pos,
                               doc = "Get/Set viewable window position")
        window_size = property(fget = __get_window_size, fset = __set_window_size,
                               doc = "Get/Set viewable window size")
        size        = property(fget = __get_size, fset = __set_size,
                                doc = "Get/Set buffer size")
        cursor      = property(fget = __get_cursor, fset = __set_cursor,
                               doc = "Get/Set cursor position")


#----------------------------------------------------------------------------------#

def get_class(): return ArrayBuffer

