from utils.Element import Element
from utils.datatypes import *

import gobject


class ConfigWidget(Element):
    """
      Abstract base class for configuration widgets. Configuration widgets can
      be directly addressed to get/set values or can be visualized to allow the
      user to change settings.
    """

    def __init__(self, name, getter, setter, caller):

        Element.__init__(self, name)

        self.__may_set_back = False
        self.__initialized = False

        self.__path = ""

        self.__getter = getter
        self.__setter = setter
        self.__caller = caller
        self.__bind = ""

        self._register_property("bind", TYPE_STRING, self._setp_bind, None,
                                "",
                                doc = "Binds the value to an object property")
        self._register_property("callback", TYPE_STRING,
                                self._setp, self._getp, None,
                                doc = "Callback function")
        self._register_property("help", TYPE_STRING, self._setp, self._getp,
                                "", doc = "Tooltip text")
        self._register_property("label", TYPE_STRING,
                                self._setp_label, self._getp, "",
                                doc = "Description label text")
        self._register_property("enabled", TYPE_BOOL,
                                self._setp_enabled, self._getp, True,
                                doc = "Whether the widget is enabled")


    def _get_path(self): return self.__path
    def set_path(self, path): self.__path = path
    


    #
    # Tells the config widget to update itself by reading from the bound object.
    #
    def update(self):

        self.__may_set_back = True

        old_value = self.get_prop("value")
        try:
            new_value = self._get_config()
        except KeyError:
            return

        if (not self.__initialized or old_value != new_value):
            self.__initialized = True
            self.set_prop("value", new_value)



    def _get_config(self):

        return self.__getter(self.__bind)


    def _set_config(self, v):
        assert self.__bind

        if (not self.__may_set_back): return

        # get_datatype_of_property() doesn't throw here, since ConfigWidget has
        # a "value" property
        datatype = self.get_datatype_of_property("value")
        self.__setter(self.__bind, v, datatype)

        self.call_callback(self.__bind, v)


    def call_callback(self, *args):

        # invoke the callback handler
        callback = self.get_prop("callback")
        if (callback):
            # we get a much better startup performance with the idle handler
            gobject.idle_add(self.__caller, callback, *args)



    def get_widgets(self): raise NotImplementedError

    def _set_enabled(self, value): raise NotImplementedError
    def _set_label(self, value): raise NotImplementedError


    def _setp_bind(self, key, value):

        self.__bind = value


    def _setp_enabled(self, key, value):

        self._setp(key, value)
        self._set_enabled(value)


    def _setp_label(self, key, value):

        self._setp(key, value)
        self._set_label(value)
