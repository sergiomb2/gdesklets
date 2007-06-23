from Vault import Vault
from main.Control import Control
from plugin.Interface import Interface


#
# Wrapper for controls.
#
class ControlWrapper(object):

    def __init__(self, control):

        self.__dict__["_ControlWrapper__control"] = Vault(control)
        self.__dict__["_ControlWrapper__properties"] = \
                     Vault( dict(Interface.get_properties(control.__class__)) )

        ids =  [ Interface.get_id(i)
                 for i in Interface.get_interfaces( control.__class__ ) ]
        taz_ids = [ Interface.get_taz_style_id(i)
                    for i in Interface.get_interfaces( control.__class__ ) ]

        self.__dict__["_ControlWrapper__ifaces_id"] = \
                                                  Vault( tuple(ids + taz_ids) )



    def __setattr__(self, name, value):

        try:
            prop = self.__properties(open)[name]
        except KeyError:
            log("Warning: Property \"%s\" isn't available." % (name,))
            return

        prop.fset(self.__control(open), value)



    def __getattr__(self, name):

        if name in Control.AUTHORIZED_METHODS:
            return getattr(self.__control(open), name)

        try:
            prop = self.__properties(open)[name]
        except KeyError:
            log("Warning: Property \"%s\" isn't available." % (name,))
            return None

        return prop.fget(self.__control(open))



    def get_interfaces_id(self):

        """
        @return : implemented interfaces' id
        @rtype : list of str
        """

        return self.__ifaces_id(open)

