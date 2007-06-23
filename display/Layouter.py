#
# Layout algorithms.
#
# A layout algorithm is a function f: (step, args) -> (x, y, relative)
# A step value of n means that the coordinates of the nth child are being
# requested.
#

class LayoutError(StandardError):
    pass


class Layouter:

    __slots__ = ('__layout',)
    __LAYOUT_TYPES = ('horizontal', 'vertical', 'grid')

    def __init__(self, layout):

        self.__layout = layout

        self.__validate_layout()



    def __validate_layout(self):

        if (not self.__layout in self.__LAYOUT_TYPES):
            log("Layout type %s isn't supported." % (self.__layout,))
            raise LayoutError



    def layout(self, step, args):

        if (self.__layout == "horizontal"):
            if (not args):
                return ("x", 0, 0)
            else:
                delta = int(args[0])
                x = delta * step
                y = 0

                return (None, x, y)

        elif (self.__layout == "vertical"):
            if (not args):
                return ("y", 0, 0)
            else:
                delta = int(args[0])
                y = delta * step
                x = 0

                return (None, x, y)

        else:
            width, deltax, deltay = args
            x = (step % int(width)) * int(deltax)
            y = (step / int(width)) * int(deltay)

            return (None, x, y)

