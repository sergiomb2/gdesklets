from main.Control import Control
from Vault import Vault
from plugin.Interface import Interface

class PropertyArray():

    # like Vault...open isn't available from the sandbox

    def __init__(self, ctrl, key = open):

        self.__dict__["_PropertyArray__key"] = Vault(key)
        self.__dict__["_PropertyArray__property"] = Vault( dict(Interface.get_properties(ctrl.__class__)) )
        #self.__dict__["_PropertyArray__control"] = Vault(ctrl)
        self._set_control(ctrl, key)



    def _set_control(self, new_ctrl, k):

        if k != self.__key(open):
            raise RuntimeError("Intrusion detected (in PropertyArray %s)" % self)

        self.__dict__["_PropertyArray__control"] = Vault(new_ctrl)



    def __setattr__(self, name, value):

        log("debug: setting %s to \'%s\'" % (name, value))
        try:
            prop = self.__property(open)[name]
        except KeyError:
            log("Warning: Property %s isn't available." % (name,))
            raise KeyError

        prop.fset(self.__control(open), value)


    def __getattr__(self, name):

        log("debug: trying to get %s" % (name,))
        if name in Control.AUTHORIZED_METHODS:
            return getattr(self.__control(open), name)

        try:
            prop = self.__property(open)[name]
        except KeyError:
            log("Warning: Property %s isn't available." % (name,))
            raise KeyError

        return prop.fget(self.__control(open))
