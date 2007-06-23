import Unit
from HashPQueue import HashPQueue


class LayoutObject(object):
    """
    gDesklets Geometry Engine
    (c) 2003 - 2005 Martin Grimme  <martin@gdesklets.org>

    This engine is licensed under the terms of the GNU LGPL.


    This class represents a layout object for handling geometry calculations
    for visual elements. It is based on the highly flexible and sophisticated
    geometry engine of gDesklets 0.34.3, but is completely decoupled from the
    rendering backend now and optimized even further.
    """

    __slots__ = ("__margin_right", "__margin_bottom", "__margin_ids",
                 "__enabled",
                 "__children", "__parent", "__relative", "__is_relative",
                 "__relatives", "__anchor",
                 "__real_geometry", "__old_real_geometry", "__geometry",
                 "__border_width", "__bbox",
                 "__geometry_callback", "__action_callback")



    def __init__(self, parent = None):
        """
        Creates a new layout object. You normally only call this for the root
        object of the hierarchy of layout objects, without specifying any parent
        object.
        """

        # right margin
        self.__margin_right = HashPQueue(HashPQueue.GREATER_THAN)

        # bottom margin
        self.__margin_bottom = HashPQueue(HashPQueue.GREATER_THAN)

        # the IDs of the margin entries
        self.__margin_ids = (-1, -1)

        # whether the element is enabled
        self.__enabled = True

        # the children of a layout object
        self.__children = []

        # the parent object
        self.__parent = parent

        # the object to which this object is placed relative to
        self.__relative = None
        self.__is_relative = (False, False)
        self.__relatives = []

        # the position of the positioning anchor given as a percentage of the
        # object's size
        self.__anchor = (0, 0)

        # the layout object's geometry
        self.__real_geometry = (Unit.ZERO, Unit.ZERO, Unit.ZERO, Unit.ZERO)
        self.__old_real_geometry = (Unit.ZERO, Unit.ZERO, Unit.ZERO, Unit.ZERO)
        self.__geometry = (Unit.Unit(), Unit.Unit(), Unit.Unit(), Unit.Unit())

        # the widths of the border
        self.__border_width = (Unit.ZERO, Unit.ZERO, Unit.ZERO, Unit.ZERO)

        # the children bounding box
        self.__bbox = (Unit.ZERO, Unit.ZERO, Unit.ZERO, Unit.ZERO)

        # the geometry callback handler
        self.__geometry_callback = None

        # the action callback handler
        self.__action_callback = None



    def new_child(self):
        """
        Creates and returns a new layout object as a child of this layout
        object. Use this method to add new objects.
        """

        child = LayoutObject(self)
        self.__children.append(child)

        return child



    def remove_child(self, child):
        """
        Removes the given child layout object. Raises a ValueError if the object
        does not exist.
        """

        self.__children.remove(child)
        rx, ry, rw, rh = child.get_real_geometry()
        self.__margin_right.remove(rx + rw)
        self.__margin_bottom.remove(ry + rh)



    def set_callback(self, handler):
        """
        Sets the callback handler for geometry changes. The callback handler
        will be invoked whenever the geometry of the object changes.

        The handler has the signature:
          handler(src, x, y, width, height)

        The callback notifies you about geometry changes of an object.
        """

        self.__geometry_callback = handler



    def set_action_callback(self, handler):

        self.__action_callback = handler



    def set_enabled(self, value):
        """
        Enables or disables the layout object. Disabled objects don't contribute
        to the layout and act as if they did not exist.
        """

        self.__enabled = value
        self._update_all()



    def set_geometry(self, x = None, y = None, width = None, height = None):
        """
        Sets the geometry values. The values have to be valid Unit objects.
        """

        gx, gy, gw, gh = self.__geometry

        if (x): gx = x
        if (y): gy = y
        if (width): gw = width
        if (height): gh = height

        self.__geometry = (gx, gy, gw, gh)
        self._update_all()



    def get_geometry(self):
        """
        Returns the user-given geometry in Unit values.
        """

        return self.__geometry



    def get_real_geometry(self):
        """
        Returns the real geometry of the object, with anchors, and relative and
        percentual positioning resolved.
        """

        return self.__real_geometry



    def _update_bbox(self, right_id, bottom_id, x, y, w, h, ignore_x, ignore_y):
        """
        Updates the bounding box with the given values.
        """

        self.__margin_right.remove(right_id)
        self.__margin_bottom.remove(bottom_id)

        right_id, bottom_id = -1, -1
        if (not ignore_x):
            right_id = self.__margin_right.insert(x.copy() + w.copy())
        if (not ignore_y):
            bottom_id = self.__margin_bottom.insert(y.copy() + h.copy())

        return (right_id, bottom_id)



    def __get_children_bbox(self):
        """
        Returns the bounding box of the child objects.
        """

        bx1 = Unit.ZERO
        by1 = Unit.ZERO
        bx2 = self.__margin_right.top() or Unit.ZERO
        by2 = self.__margin_bottom.top() or Unit.ZERO
        return (bx1, by1, bx2, by2)



    def __get_parent_size(self):
        """
        Returns the size of the parent widget.
        """

        parent_width, parent_height = \
                      self.__parent.get_real_geometry()[2:]

        # don't allow dangerous values for the parent's size
        parent_width = max(Unit.ONE, parent_width)
        parent_height = max(Unit.ONE, parent_height)
        return (parent_width, parent_height)



    def set_anchor(self, x, y):
        """
        Sets the positioning anchor to the given place. The coordinates are
        given in percentages of the object's size with values between 0.0
        and 1.0.
        """

        self.__anchor = (x, y)
        self._update_all()



    def get_anchor(self):
        """
        Returns the position of the anchor.
        """

        return self.__anchor



    def __is_percentual(self):
        """
        Returns whether the object has some percentual values.
        """

        x, y, w, h = self.__geometry
        return Unit.UNIT_PERCENT in (x.get_unit(), y.get_unit(),
                                     w.get_unit(), h.get_unit())



    def __resolve_anchor(self, x, y, w, h):
        """
        Resolves the anchored position and returns the position of the top-left
        corner of the object.
        """

        ax, ay = self.get_anchor()
        ax = w * ax
        ay = h * ay
        return (x - ax, y - ay)



    def _update_all(self):
        """
        Updates the geometry of the layout object and adjusts depending objects
        as well.
        """

        if (self._update_geometry()):
            self._update_relatives()
            self._update_children()
            self._update_parent()

            # objects with percentual geometry sometimes need special treatment
            if (self.__is_percentual()):
                if (self._update_geometry()):
                    self._update_relatives()

        else:
            self._update_children()


    def _update_geometry(self):
        """
        Updates the geometry of the layout object.
        This does not include notifying the parent object or relative objects
        about the change.

        Returns True if something changed, False otherwise.
        """

        x, y, w, h = self.__real_geometry
        ux, uy, uw, uh = self.__geometry

        # adjust percentage stuff
        if (self.__parent):
            parent_width, parent_height = self.__get_parent_size()
            w1, h1, w2, h2 = self.__parent.get_border_width()
            pw = parent_width - w1 - w2
            ph = parent_height - h1 - h2
            parent_width = (pw >= Unit.ZERO) and pw or Unit.ZERO
            parent_height = (ph >= Unit.ZERO) and ph or Unit.ZERO

            if (parent_width.is_unset()): parent_width = w
            if (parent_height.is_unset()): parent_height = h

            ux.set_100_percent(parent_width.as_px())
            uw.set_100_percent(parent_width.as_px())
            uy.set_100_percent(parent_height.as_px())
            uh.set_100_percent(parent_height.as_px())

        # compute geometry
        if (ux.is_unset()): new_x = x
        else: new_x = ux

        if (uy.is_unset()): new_y = y
        else: new_y = uy

        if (self.__enabled):
            if (uw.is_unset()): new_w = self.__get_value_for_unset(width = w)
            else: new_w = uw

            if (uh.is_unset()): new_h = self.__get_value_for_unset(height = h)
            else: new_h = uh

        else:
            new_w = Unit.ZERO
            new_h = Unit.ZERO

        # handle relative positioning
        if (self.__relative):
            is_rel_x, is_rel_y = self.__is_relative

            # get the coords of the anchor of the relative
            rx, ry, rw, rh = self.__relative.get_real_geometry()
            anchor_x, anchor_y = self.__relative.get_anchor()
            anchor_x = rw * anchor_x
            anchor_y = rh * anchor_y

            # get the remaining amount of pixels from the anchor to the
            # bottom/right edge of the relative
            tw = rw - anchor_x
            th = rh - anchor_y

            if (not ux.is_unset()): new_x += rx + anchor_x
            else: new_x = rx + anchor_x
            if (not uy.is_unset()): new_y += ry + anchor_y
            else: new_y = ry + anchor_y
            if (is_rel_x): new_x += tw
            if (is_rel_y): new_y += th
        #end if

        # get coords of the top left corner, i.e. resolve the anchor
        new_x, new_y = self.__resolve_anchor(new_x, new_y, new_w, new_h)

        old_x, old_y, old_w, old_h = self.__old_real_geometry
        if ((new_x, new_y, new_w, new_h) != self.__old_real_geometry):
            self.__real_geometry = (new_x.copy(), new_y.copy(),
                                    new_w.copy(), new_h.copy())
            self.__old_real_geometry = (new_x.copy(), new_y.copy(),
                                        new_w.copy(), new_h.copy())

            # update the parent's children bounding box
            if (self.__parent):
                right_id, bottom_id = self.__margin_ids
                ignore_x = (Unit.UNIT_PERCENT in
                            (ux.get_unit(), uw.get_unit()))
                ignore_y = (Unit.UNIT_PERCENT in
                            (uy.get_unit(), uh.get_unit()))
                self.__margin_ids = \
                        self.__parent._update_bbox(right_id, bottom_id,
                                                   new_x, new_y, new_w, new_h,
                                                   ignore_x, ignore_y)

            # call the geometry callback
            if (self.__geometry_callback):
                self.__geometry_callback(self, new_x, new_y, new_w, new_h)

            return True

        else:
            return False



    def _update_relatives(self):
        """
        Updates the geometry of the objects placed relative to this object.
        """

        for r in self.__relatives:
            r._update_geometry()
            r._update_relatives()



    def _update_children(self):
        """
        Updates the geometry of the child objects of this object. This only
        affects children with percentual geometry values.
        """

        if (not self.__enabled): return
        x, y, w, h = self.get_geometry()
        for c in self.__children:
            ux, uy, uw, uh = c.get_geometry()
            if (Unit.UNIT_PERCENT in (ux.get_unit(), uy.get_unit(),
                                      uw.get_unit(), uh.get_unit())):
                c._update_geometry()
                c._update_relatives()
                c._update_children()
        #end for



    def _update_parent(self):
        """
        Updates the geometry of the parent object. This only affects the parent
        if it does not have a fixed size.
        """

        if (self.__parent):
            x, y, w, h = self.__parent.get_geometry()
            if (Unit.Unit() in (w, h)):
                self.__parent._update_all()



    def set_relative_to(self, other, is_rel_x, is_rel_y):
        """
        Places the object relative to another one.
        """

        self.__relative = other
        self.__is_relative = (is_rel_x, is_rel_y)
        other._add_relative(self)
        self._update_all()



    def _add_relative(self, r):
        """
        Adds a new relative object.
        """

        self.__relatives.append(r)



    def _remove_relative(self, r):
        """
        Removes a relative object.
        """

        try:
            self.__relatives.remove(r)
        except:
            pass



    def set_border_width(self, left, top, right, bottom):
        """
        Sets the widths of the four borders of the layout object.
        A border-width > 0 results in inner padding.
        """

        self.__border_width = (left, top, right, bottom)
        self._update_all()



    def get_border_width(self):
        """
        Returns the widths of the four borders as a 4-tuple.
        """

        return self.__border_width



    def __get_value_for_unset(self, x = None, y = None,
                             width = None, height = None):
        """
        Returns the geometry value that should be used for unset values.
        """

        bx1, by1, bx2, by2 = self.__get_children_bbox()
        bw1, bh1, bw2, bh2 = self.__border_width

        if (x): return x
        elif (y): return y
        elif (width): return bx2 + bw1 + bw2
        elif (height): return by2 + bh1 + bh2



    def send_action(self, x, y, *args):

        if (self.__action_callback):
            self.__action_callback(self, x, y, *args)

        bw, bh, nil, nil = self.__border_width
        x -= bw
        y -= bh

        for c in self.__children:
            cx, cy, cw, ch = c.get_real_geometry()
            if (cx <= x < cx + cw and cy <= y < cy + ch):
                c.send_action(x - cx, y - cy, *args)
        #end for



    def dump(self, indent = 0):
        """
        For debugging:
        Dumps the geometry values of the layout object together with all
        child-objects to stdout.
        """

        print " " * indent,
        print self.get_geometry(), "---", \
              map(lambda f: f.as_px(), self.get_real_geometry())
        for c in self.__children:
            c.dump(indent + 2)



if (__name__ == "__main__"):

    help(LayoutObject)

    def on_action(src, x, y, arg):

        print x, y, arg


    def on_change(src, x, y, w, h):

        print src
        print "  ", x, y, w, h


    r = LayoutObject()
    r.set_geometry(Unit.ZERO, Unit.ZERO,
                   Unit.Unit(1280, Unit.UNIT_PT), Unit.Unit(1024, Unit.UNIT_PT))
    a = r.new_child()

    a.set_geometry(Unit.Unit(50, Unit.UNIT_PERCENT),
                   Unit.Unit(10, Unit.UNIT_PERCENT),
                   Unit.Unit(), Unit.Unit())
    a.set_border_width(Unit.Unit(10, Unit.UNIT_PX),
                       Unit.Unit(10, Unit.UNIT_PX),
                       Unit.Unit(10, Unit.UNIT_PX),
                       Unit.Unit(10, Unit.UNIT_PX))

    for x in range(0, 7):
        for y in range(0, 5):
            new = a.new_child()
            new.set_callback(on_change)
            new.set_action_callback(on_action)
            new.set_geometry(Unit.Unit(x, Unit.UNIT_PT),
                             Unit.Unit(y, Unit.UNIT_PT),
                             Unit.Unit(50, Unit.UNIT_PT),
                             Unit.Unit(10, Unit.UNIT_PT))
            new.set_anchor(1.0, 0.2)

    print a.get_real_geometry()
    a.send_action(Unit.Unit(5, Unit.UNIT_PT),
                  Unit.Unit(4, Unit.UNIT_PT), "test")
