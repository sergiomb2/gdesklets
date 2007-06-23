#
# Class for settings for data targets.
#

class TargetSettings(dict):

    __slots__ = ()

    set = dict.__setitem__
    get_entries = dict.items

