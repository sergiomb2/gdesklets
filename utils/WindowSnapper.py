from utils.BinTree import BinTree

import gtk


def _cmp_equal(this, other):

    return cmp(this, other)


def _cmp_notequal(this, other):

    return cmp(this, other) or 1


def _cmp_snap(this, other):

    u, ua, ub = this
    v, va, vb = other

    if (abs(u - v) < 8):
        if (va <= ua <= vb or va <= ub <= vb or
            ua <= va <= ub or ua <= vb <= ub):
            return 0

    if (u < v): return -1
    else: return 1


#
# Class for snapping windows together.
#
class WindowSnapper(object):

    __slots__ = ('__horiz', '__vertic')

    def __init__(self):

        self.__horiz = BinTree()
        self.__vertic = BinTree()

        self.__horiz.insert((0, 0, gtk.gdk.screen_height()), _cmp_notequal)
        self.__horiz.insert((gtk.gdk.screen_width(),
                             0, gtk.gdk.screen_height()), _cmp_notequal)
        self.__vertic.insert((0, 0, gtk.gdk.screen_width()), _cmp_notequal)
        self.__vertic.insert((gtk.gdk.screen_height(),
                             0, gtk.gdk.screen_width()), _cmp_notequal)


    def insert(self, x, y, w, h):

        self.__horiz.insert((x, y, y + h), _cmp_notequal)
        self.__horiz.insert((x + w, y, y + h), _cmp_notequal)
        self.__vertic.insert((y, x, x + w), _cmp_notequal)
        self.__vertic.insert((y + h, x, x + w), _cmp_notequal)


    def remove(self, x, y, w, h):

        self.__horiz.remove((x, y, y + h), _cmp_equal)
        self.__horiz.remove((x + w, y, y + h), _cmp_equal)
        self.__vertic.remove((y, x, x + w), _cmp_equal)
        self.__vertic.remove((y + h, x, x + w), _cmp_equal)


    def snap(self, x, y, w, h):

        value1 = self.__horiz.find((x, y, y + h), _cmp_snap)
        value2 = self.__horiz.find((x + w, y, y + h), _cmp_snap)
        value3 = self.__vertic.find((y, x, x + w), _cmp_snap)
        value4 = self.__vertic.find((y + h, x, x + w), _cmp_snap)

        new_x = x
        new_y = y
        if (value1):
            new_x = value1[0]
        elif (value2):
            new_x2 = value2[0]
            new_x = new_x2 - w
        if (value3):
            new_y = value3[0]
        elif (value4):
            new_y2 = value4[0]
            new_y = new_y2 - h

        return (new_x, new_y)
