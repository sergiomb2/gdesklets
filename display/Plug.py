from main import UNSET_COORD

import gtk


#
# Container class for displays that are pluggable into other applications.
#
class Plug(gtk.Plug):

    def __init__(self):

        # window size for detecting resizing
        self.__window_size = (0, 0)

        self.__shape = None

        gtk.Plug.__init__(self, 0L)

        self.set_size_request(-1, -1)
        self.set_default_size(10, 10)

        # set up event handlers
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK)



    #
    # Returns the XEMBED ID for embedding this plug into other applications.
    #
    def get_xembed_id(self):

        return self.get_id()



    def close(self):

        self.destroy()



    def set_position(self, x, y):

        # we happily ignore this
        pass



    def set_size(self, width, height):

        self.resize(width, height)



    def set_window_flags(self, value):

        # we happily ignore this
        pass



    def set_shape(self, mask):

        if (self.__window_pos == (UNSET_COORD, UNSET_COORD)):
            self.__shape = mask
        else:
            self.shape_combine_mask(mask, 0, 0)
