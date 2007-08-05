from ConfigDialog import ConfigDialog
from StateSaver import StateSaver
from utils.datatypes import *


class DisplayConfigger(ConfigDialog):
    """
      Configuration Dialog for the displays. This class handles loading / saving
      the configuration.
    """

    def __init__(self, ident, path):

        # init the StateSaver
        self.__backend = StateSaver(ident + "CONFIG")

        # may we save already, or is it too early?
        self.__may_save = False

        # ID for storing the configuration
        self.__ident = ident

        # the scripting environment with which the config interacts
        self.__scripting_environment = None

        ConfigDialog.__init__(self, path)
        self.set_property("title", _("Configuration"))



    #
    # Sets the scripting environment to be used.
    #
    def set_scripting_environment(self, script):

        self.__scripting_environment = script
        self._set_setter(self.__setter_wrapper)
        self._set_getter(self.__scripting_environment.get_value)
        self._set_caller(self.__scripting_environment.call_function)



    #
    # Wraps the config setter handler to include saving config.
    #
    def __setter_wrapper(self, key, value, datatype):
        assert key

        self.__scripting_environment.set_value(key, value)

        # save config, but not too early
        if (self.__may_save):
            rep = dtype_repr(datatype, value)
            self.__backend.set_key(key, (rep, dtype_name(datatype)))



    #
    # Build preferences and put elements into the scripting environment
    #
    def build(self, items):

        ConfigDialog.build(self, items)

        for c in self.get_config_items():
            ident = c.get_prop("id")
            if (ident):
                self.__scripting_environment.add_element("Prefs", ident, c)



    #
    # Loads the initial configuration.
    #
    def load_config(self):

        # read stored configuration
        for key in self.__backend.list():
            if (key.endswith("_TYPE")): continue

            rep, dtype = self.__backend.get_key(key)
            datatype = dtype_get_type(dtype)
            value = dtype_build(datatype, rep)

            try:
                self.__setter_wrapper(key, value, None)
            except:
                log("Couldn't pass arguments (%s, %s) to setter."
                    % (key, value))

        # have the children update themselves
        for c in self.get_config_items(): c.update()



    #
    # Removes the configuration.
    #
    def remove_config(self):

        self.__backend.remove()



    def show(self):

        self.__may_save = True
        ConfigDialog.show(self)
