from main.Control import Control
from Vault import Vault
from plugin.Interface import Interface

class PropertyInterface():

    def __init__(self, ctrl):

        self.__dict__["_PropertyInterface__property"] = Vault( dict(Interface.get_properties(ctrl.__class__)) )
        self.__dict__["_PropertyInterface__control"] = Vault(ctrl)



    def __setattr__(self, name, value):

        try:
            prop = self.__property(open)[name]
        except KeyError:
            log("Warning: Property %s isn't available." % (name,))
            raise KeyError

        prop.fset(self.__control(open), value)



    def __getattr__(self, name):

        if name in Control.AUTHORIZED_METHODS:
            return getattr(self.__control(open), name)

        try:
            prop = self.__property(open)[name]
        except KeyError:
            log("Warning: Property %s isn't available." % (name,))
            raise KeyError

        return prop.fget(self.__control(open))
