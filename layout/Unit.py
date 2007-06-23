from config import settings

class _UNIT(str): pass

# for now, we can't use _UNIT() yet; there is some code to be modified first
UNIT_CM = "cm" #_UNIT("cm")
UNIT_IN = "in" #_UNIT("in")
UNIT_PERCENT = "%" #_UNIT("%")
UNIT_PT = "pt" #_UNIT("pt")
UNIT_PX = "px" #_UNIT("px")


def _round(v): return (v < 0) and int(v - 0.5) or int(v + 0.5)


class Unit(object):
    """
      Class for coordinate and size values with units. This class abstracts from
      actual lengths with concrete units.
    """

    __slots__ = ('__is_unset', '__unit', '__cache_px', '__cache_pt',
                 '__cache_cm', '__cache_in', '__cache_pcnt', '__in2pcnt',
                 '__original_value', '__value', '__percent_size',
                 '__IN2PT_SCALE', '__PT2IN_SCALE', '__IN2PX_SCALE',
                 '__PX2IN_SCALE', '__IN2CM_SCALE', '__CM2IN_SCALE')


    def __init__(self, value = None, unit = None, string = None):

        self.__percent_size = 0

        # scaling factors
        self.__IN2PT_SCALE = 72.0
        self.__PT2IN_SCALE = 1 / self.__IN2PT_SCALE
        self.__IN2PX_SCALE = float(settings.dpi)
        self.__PX2IN_SCALE = 1 / self.__IN2PX_SCALE
        self.__IN2CM_SCALE = 2.54
        self.__CM2IN_SCALE = 1 / self.__IN2CM_SCALE

        if (not string): string = None
        if (value == unit == string == None):
            value, unit = 0, UNIT_PX
            self.__is_unset = True
        else:
            self.__is_unset = False

        if (string):
            if (string.endswith("%")):
                value = float(string[:-1])
                unit = UNIT_PERCENT
            elif (string.endswith("cm")):
                value = float(string[:-2])
                unit = UNIT_CM
            elif (string.endswith("in")):
                value = float(string[:-2])
                unit = UNIT_IN
            elif (string.endswith("pt")):
                value = float(string[:-2])
                unit = UNIT_PT
            else:
                try:
                    value = int(float(string))
                except ValueError:
                    unit = "".join([c for c in string if c.isalpha()])
                    log("Unit \"%s\" isn't supported, using \"0px\"." % unit)
                    value = 0
                unit = UNIT_PX


        # the unit type
        self.__unit = unit

        # cache for computed values
        self.__cache_px = (unit == UNIT_PX) and value or None
        self.__cache_pt = (unit == UNIT_PT) and value or None
        self.__cache_cm = (unit == UNIT_CM) and value or None
        self.__cache_in = (unit == UNIT_IN) and value or None
        self.__cache_pcnt = (unit == UNIT_PERCENT) and value or None

        # the scaling factor from inches to percentage
        self.__in2pcnt = 0.1

        # store value in inches
        self.__original_value = value
        self.__value = self.__unit_to_inch(value, unit)
        self.set_100_percent(100)


    def __unit_to_inch(self, value, unit):

        if (unit == UNIT_IN): return value
        elif (unit == UNIT_CM): return value * self.__CM2IN_SCALE
        elif (unit == UNIT_PX): return value * self.__PX2IN_SCALE
        elif (unit == UNIT_PT): return value * self.__PT2IN_SCALE
        # percentual values get converted at a later time
        elif (unit == UNIT_PERCENT): return value


    def __inch_to_unit(self, value, unit):

        if (unit == UNIT_IN):
            v = value
            self.__cache_in = v
        elif (unit == UNIT_CM):
            v = value * self.__IN2CM_SCALE
            self.__cache_cm = v
        elif (unit == UNIT_PX):
            v = _round(value * self.__IN2PX_SCALE)
            self.__cache_px = v
        elif (unit == UNIT_PT):
            v = value * self.__IN2PT_SCALE
            self.__cache_pt = v
        elif (unit == UNIT_PERCENT):
            v = value * self.__in2pcnt
            self.__cache_pcnt = v

        return v


    def set_100_percent(self, size):

        if (size <= 0): size = 1

        self.__percent_size = size
        # size is a value in pixels, therefore convert it to inches
        size = self.__unit_to_inch(size, UNIT_PX)

        if (self.__unit == UNIT_PERCENT):
            self.__value = (self.__original_value) * (size / 100.0)

        self.__in2pcnt = 100.0 / size

        # invalidate cached values
        self.__cache_pcnt = None
        self.__cache_px = None
        self.__cache_pt = None
        self.__cache_cm = None
        self.__cache_in = None


    def get_100_percent(self):

        return self.__in2pcnt


    def as_px(self):
        return self.__cache_px or self.__inch_to_unit(self.__value, UNIT_PX)

    def as_pt(self):
        return self.__cache_pt or self.__inch_to_unit(self.__value, UNIT_PT)

    def as_cm(self):
        return self.__cache_cm or self.__inch_to_unit(self.__value, UNIT_CM)

    def as_in(self):
        return self.__cache_in or self.__inch_to_unit(self.__value, UNIT_IN)

    def as_percent(self):
        return self.__cache_pcnt or self.__inch_to_unit(self.__value,
                                                        UNIT_PERCENT)

    def get_unit(self): return self.__unit
    def is_unset(self): return self.__is_unset


    #
    # Creates a new Unit object as a copy of this one.
    #
    def copy(self):

        new = Unit(self.as_pt(), UNIT_PT)
        new.set_100_percent(self.__percent_size)
        return new


    def __getitem__(self, unit):

        log("Deprecation:\n"
            "Accessing the Unit object as a dictionary is deprecated. "
            "Please use the appropriate accessor methods instead.", True)

        return self.__inch_to_unit(self.__value, unit)


    def __add__(self, other):

        return Unit(self.as_pt() + other.as_pt(), UNIT_PT)


    def __sub__(self, other):

        return Unit(self.as_pt() - other.as_pt(), UNIT_PT)


    def __mul__(self, other):

        if (isinstance(other, Unit)):
            return Unit(self.as_pt() * other.as_pt(), UNIT_PT)
        else:
            return Unit(self.as_pt() * other, UNIT_PT)


    def __div__(self, other):

        if (isinstance(other, Unit)):
            return Unit(self.as_pt() / other.as_pt(), UNIT_PT)
        else:
            return Unit(self.as_pt() / other, UNIT_PT)


    def __cmp__(self, other):
        assert (other == None or isinstance(other, Unit)), \
               "Cannot compare with non-Unit object"

        if (not other): return 1
        else: return cmp(int(self.as_pt()), int(other.as_pt()))


    def __repr__(self):
        unit = self.get_unit()
        if (self.is_unset()): return "unset"
        if (unit == UNIT_CM): return "%fcm" % self.as_cm()
        elif (unit == UNIT_IN): return "%fin" % self.as_in()
        elif (unit == UNIT_PT): return "%fpt" % self.as_pt()
        elif (unit == UNIT_PX): return "%f" % self.as_px()
        elif (unit == UNIT_PERCENT): return "%f%%" % self.as_percent()


    def __hash__(self):

        return hash(repr(self))

import sys
# for convenience
ZERO = Unit(0, UNIT_PT)
ONE = Unit(1, UNIT_PT)
MAXIMUM = Unit(sys.maxint, UNIT_PT)
UNSET = Unit()


if (__name__ == "__main__"):

    u = Unit(10, UNIT_PX)
    u.set_100_percent(11)
    print u.as_px()
    print u.as_in()
    print u.as_percent()
