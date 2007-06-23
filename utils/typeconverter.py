from main import USERHOME
from datatypes import *
from layout import Unit
import pwstore


def str2type(dtype, value):

    if (dtype == TYPE_STRING):
        return value

    elif (dtype == TYPE_SECRET_STRING):
        return pwstore.retrieve(USERHOME, value)

    elif (dtype == TYPE_BOOL):
        return (value in ("True", "true", "1", "1L"))

    elif (dtype == TYPE_INT):
        return int(value)

    elif (dtype == TYPE_FLOAT):
        return float(value)

    elif (dtype == TYPE_LIST):
        v = value.replace("\\,", "@@COMMA@@")
        parts = v.split(",")
        return [ p.strip().replace("@@COMMA@@", ",") for p in parts ]

    elif (dtype == TYPE_UNIT):
        return Unit.Unit(string = value)

    elif (dtype == TYPE_UNIT_LIST):
        parts = value.split(",")
        return [ str2type(TYPE_UNIT, unit.strip()) for unit in parts ]

    else:
        return value


#
# This method is only used by Sensor and is thus deprecated.
#
def type2str(dtype, value):

    if (dtype == TYPE_LIST and isinstance(value, list)):
        return ",".join(value)

    elif (dtype == TYPE_SECRET_STRING):
        return pwstore.store(USERHOME, value)

    elif (dtype == TYPE_BOOL):
        return value and "true" or "false"

    elif (dtype == TYPE_UNIT):
        val, unit = value
        if (unit != UNIT_PX): return str(val) + unit
        else: return str(val)

    else:
        return str(value)
