from Vault import Vault
from PropertyArray import PropertyArray
from main.Control import Control
from plugin.Interface import Interface
from copy import deepcopy

#
# Wrapper for controls.
#
class ControlWrapper(object):

    def __init__(self, control, size=0):

        # Don't think it matters if the sandbox can see the length of this (in
        # fact, isn't that what's desired?)
        self.__dict__["length"] = size
        array_size = size
        if size == 0:
            array_size = 1

        # We need to deepcopy in order to get individually changeable
        # Control instances
        self.__dict__["_ControlWrapper__control"] = \
                     Vault( [ deepcopy(control)
                              for i in range(array_size) ] )
        self.__dict__["_ControlWrapper__properties"] = \
                     dict([ (k, PropertyArray(v, self.__dict__["_ControlWrapper__control"], array_size))
                                   for (k, v) in Interface.get_properties(control.__class__) ])

        ids =  [ Interface.get_id(i)
                 for i in Interface.get_interfaces( control.__class__ ) ]
        taz_ids = [ Interface.get_taz_style_id(i)
                    for i in Interface.get_interfaces( control.__class__ ) ]

        self.__dict__["_ControlWrapper__ifaces_id"] = \
                                                  Vault( tuple(ids + taz_ids) )



    def __setattr__(self, name, value):

        if name == "length":
            if self.__dict__["length"] == 0:
                self.__dict__["length"] = 1

            while value > self.__dict__["length"]:
                #TODO: implement deletion
                self.__control(open)[name].append(self.__control(open)[0])
                self.__properties(open)[name].append(self.__properties(open)[name][0])
                self.__dict__["length"] += 1
        else: # name != "length"
            if self.__dict__["length"] == 0:
                try:
                    prop = self.__properties[name][0]
                except KeyError:
                    log("Warning: Property \"%s\" isn't available." % (name,))
                    return

                prop.fset(self.__control(open)[0], value)
            else: # length != 0
                try:
                    self.__properties[name]
                except KeyError:
                    log("Warning: Property \"%s\" isn't available." % (name,))
                    return

                log("Warning: Property \"%s\" must be indexed." % (name,))
                return



    def __getattr__(self, name):

        if name in Control.AUTHORIZED_METHODS:
            if self.__dict__["length"] == 0:
                return getattr(self.__control(open)[0], name)
            else:
                return self.__control(open)

        if name == "length":
            return self.length
        elif self.__dict__["length"] == 0:
            try:
                prop = self.__properties[name][0]
            except KeyError:
                log("Warning: Property \"%s\" isn't available." % (name,))
                return None

            return prop.fget(self.__control(open)[0])
        else:
            return self.__properties[name]



    def get_interfaces_id(self):

        """
        @return : implemented interfaces' id
        @rtype : list of str
        """

        return self.__ifaces_id(open)

