"""
This module holds the datatypes known to gDesklets.
Datatypes are structs containing the type name and some functions for working
with types.

This module further contains some helper functions for dealing with datatypes.

A datatype consists of:
  - name
  - type checker function to check the type of the given value
  - representation function to get a storable representation of the given value
  - build function to build a value from the given representation

"""



TYPE_UNKNOWN = (
    "unknown",                              # name
    lambda v: True,                         # type checker
    lambda v: repr(v),                      # get representation
    lambda r: r                             # build from representation
    )

TYPE_ANY = (
    "any",
    lambda v: True,
    lambda v: repr(v),
    lambda r: r
    )

TYPE_STRING = (
    "string",
    lambda v: type(v) in (type(""), type(u"")),
    lambda v: v,
    lambda r: r
)

TYPE_INT = (
    "integer",
    lambda v: type(v) in (type(1), type(1L)),
    lambda v: str(v),
    lambda r: int(r)
    )

TYPE_FLOAT = (
    "float",
    lambda v: type(v) in (type(0.5), type(1), type(1L)),
    lambda v: str(v),
    lambda r: float(r)
    )

TYPE_LIST = (
    "list",
    lambda v: type(v) in (type([]), type(())),
    lambda v: repr(v),
    lambda r: list(v)
    )

TYPE_BOOL = (
    "bool",
    lambda v: type(v) in (type(True), type(1), type(1L)),
    lambda v: v,
    lambda r: r
    )

from layout.Unit import Unit as _Unit
TYPE_UNIT = (
    "unit",
    lambda v: isinstance(v, _Unit),
    lambda v: repr(v),
    lambda r: _Unit(string = r)
    )

TYPE_UNIT_LIST = (
    "unit list",
    lambda v: isinstance(v[0], _Unit),
    lambda v: repr(v),
    lambda r: r
    )

TYPE_SECRET_STRING = (
    "secret string",
    lambda v: type(v) == type("")
    )

TYPE_OBJECT = (
    "object",
    lambda v: True  # anything matches
    )



def dtype_get_type(name):
    """Returns the datatype with the given name or TYPE_UNKNOWN if the type does
       not exist."""

    for dtype in ( TYPE_ANY, TYPE_STRING, TYPE_INT,
                   TYPE_FLOAT, TYPE_LIST, TYPE_BOOL,
                   TYPE_UNIT, TYPE_UNIT_LIST ):
        if (dtype_name(dtype) == name):
            return dtype
    #end for

    return TYPE_UNKNOWN


def dtype_name(dtype): return dtype[0]
def dtype_check(dtype, v): return dtype[1](v)
def dtype_repr(dtype, v): return dtype[2](v)
def dtype_build(dtype, r): return dtype[3](r)


def dtype_guess(value):
    """Guesses and returns the datatype of the given value."""

    for dtype in ( TYPE_UNIT, TYPE_LIST, TYPE_BOOL,
                   TYPE_STRING, TYPE_INT, TYPE_FLOAT,
                   TYPE_UNKNOWN ):
        if (dtype_check(dtype, value)): return dtype

    #end for

    # never reached since TYPE_UNKNOWN always matches
    assert False
