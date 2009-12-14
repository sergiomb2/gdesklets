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

        self.__dict__["_ControlWrapper__length"] = size
        # can we just use the 'size' variable?
        array_size = size
        if size == 0:
            array_size = 1

        # We need to deepcopy in order to get individually changeable
        # Control instances
        self.__dict__["_ControlWrapper__control"] = \
                     Vault( [ deepcopy(control)
                              for i in range(array_size) ] )
        # Keep a an original copy around for extending the array
        self.__dict__["_ControlWrapper__original_control"] = Vault(control)
        # This creates a dictionary of property arrays accesible by the keys
        # normally used to access the property
        self.__dict__["_ControlWrapper__properties"] = \
                     dict([ (k, PropertyArray(v, self.__control, array_size))
                                    for (k, v) in Interface.get_properties(control.__class__) ])

        ids =  [ Interface.get_id(i)
                 for i in Interface.get_interfaces( control.__class__ ) ]
        taz_ids = [ Interface.get_taz_style_id(i)
                    for i in Interface.get_interfaces( control.__class__ ) ]

        self.__dict__["_ControlWrapper__ifaces_id"] = \
                                                  Vault( tuple(ids + taz_ids) )



    def __len__(self):

        return self.__length



    def __setattr__(self, name, value):

        if name == "length":
            # A little bounds checking
            if value <= 0:
              log("Warning: Value of property \"length\" must be greater than 0 (setting to 1)")
              value = 1

            # Don't do anything if value isn't changing
            if value != self.__length:
                if value > self.__length:
                    self.__dict__["_ControlWrapper__control"] = \
                        Vault( self.__control(open) +           \
                               [ deepcopy(self.__original_control(open))  \
                                 for i in range(self.__length, value) ] )
                elif value < self.__length:
                    # We want to leave the "0th" item alone
                    # Handled by the above conditionals
                    start_deleting_at = value #if value != 0 else 1
                    c = self.__control(open)
                    for i in range(start_deleting_at, self.__length):
                        del c[i]
                    self.__dict__["_ControlWrapper__control"] = Vault(c)

                # Pass on the value to each item in the PropertyArray
                for k in self.__properties.keys():
                    # Reset the PropertyArray's control element
                    self.__properties[k]._set_control(self.__control, open)
                    self.__properties[k]._set_length(value, open)
                self.__dict__["_ControlWrapper__length"] = value
        else: # name != "length"
            # Backwards compatibility
            if self.__length == 1:
                try:
                    prop = self.__properties[name][0]
                except KeyError:
                    log("Warning: Property \"%s\" isn't available." % (name,))
                    return

                prop.fset(self.__control(open)[0], value)
            # This is the case where someone tries to access a property
            # of this class when the length != 1. They should know
            # better if they've gone and changed the length, but we'll
            # be nice and print out some informational warnings.
            else: # length != 1
                try:
                    prop = self.__properties[name]
                except KeyError:
                    log("Warning: Property \"%s\" isn't available." % (name,))
                finally:
                    log("Warning: Property \"%s\" must be indexed (length != 0)." % (name,))
                    return



    def __getattr__(self, name):

        if name in Control.AUTHORIZED_METHODS:
            if self.__length == 0:
                return getattr(self.__control(open)[0], name)
            else:
                return self.__control(open)

        # This is where the magic happens.
        # The __properties dict has its own locking mechanisms, so
        # just give the whole thing to the user.
        if name == "length":
            return self.__length
        else:
            return self.__properties[name]



    def get_interfaces_id(self):

        """
        @return : implemented interfaces' id
        @rtype : list of str
        """

        return self.__ifaces_id(open)

