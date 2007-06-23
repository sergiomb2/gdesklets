from ConfigFloat import ConfigFloat
from utils.datatypes import *


class ConfigInteger(ConfigFloat):

    def __init__(self, name, getter, setter, caller):

        ConfigFloat.__init__(self, name, getter, setter, caller,
                             int_only = True)

        self._register_property("value", TYPE_INT, self._setp_value,
                                self._getp, 0.0, doc = "Value")
