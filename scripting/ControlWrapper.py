from Vault import Vault
from PropertyInterface import PropertyInterface
from main.Control import Control
from plugin.Interface import Interface
from copy import deepcopy

#
# Wrapper for controls.
#
class ControlWrapper(object):

    def __init__(self, control, size):

        self.__dict__["_ControlWrapper__length"] = size
        # Use 'array_size' so the PropertyInterface constructor gets the
        # original setting
        array_size = size
        if size <= 0:
            array_size = 1

        # We need to deepcopy in order to get individually changeable
        # Control instances
        self.__dict__["_ControlWrapper__control"] = \
                     Vault( [ deepcopy(control)
                              for i in range(array_size) ] )
        # Keep an original copy around for extending the array
        self.__dict__["_ControlWrapper__original_control"] = Vault(control)
        # Create a property handler for each deep copy of control
        self.__dict__["_ControlWrapper__properties"] = \
                     [ PropertyInterface(self.__control(open)[i])
                       for i in range(array_size) ]

        ids =  [ Interface.get_id(i)
                 for i in Interface.get_interfaces( control.__class__ ) ]
        taz_ids = [ Interface.get_taz_style_id(i)
                    for i in Interface.get_interfaces( control.__class__ ) ]

        self.__dict__["_ControlWrapper__ifaces_id"] = \
                                                  Vault( tuple(ids + taz_ids) )



    def __len__(self):

        return self.__length



    def __setattr__(self, name, value):

        log("debug: trying to set %s to %s" % (name, value))
        if self.__length > 0:

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
                                   [ deepcopy(self.__original_control(open))    \
                                     for i in range(self.__length, value) ] )
                        self.__dict__["_ControlWrapper__properties"] = \
                            self.__properties +                        \
                            [ PropertyInterface(self.__control(open)[i])    \
                              for i in range(self.__length, value) ]
                    elif value < self.__length:
                        # We want to leave the "0th" item alone, which is 
                        # handled by the above conditionals
                        start_deleting_at = value #if value != 0 else 1
                        for i in range(start_deleting_at, self.__length):
                            del self[i]

                    self.__dict__["_ControlWrapper__length"] = value
            else: # name != "length"
                # This is the case where someone tries to set a property
                # of this class when the length != 0. They should know
                # better if they've gone and changed the length, but we'll
                # be nice and print out some informational warnings.
                log("Warning: Property \"%s\" must be indexed (length == %d)." % (name, self.__length))
                return

        else: # length <= 0

            # Backwards compatibility
            self.__dict__["_ControlWrapper__properties"][0][name] = value



    def __getattr__(self, name):

        log("debug: trying to get %s" % (name,))
        print self.__control(open)
        if name in Control.AUTHORIZED_METHODS:
            if self.__length <= 0:
                return getattr(self.__control(open)[0], name)
            else:
                return self.__control(open)

        if self.__length <= 0:
            # Backwards compatibility
            return self.__properties[0][name]
        elif name == "length":
            return self.__length
        else:
            print "debug: length: %d" % self.__length
            # This is the case where someone tries to set a property
            # of this class when the length != 0. They should know
            # better if they've gone and changed the length, but we'll
            # be nice and print out some informational warnings.
            log("Warning: Property \"%s\" must be indexed (length == %d)." % (name, self.__length))
            return



    def __setitem__(self, idx, value):

        if self.__length <= 0:

            log("Warning: Control not initialized as an array.")
            raise IndexError

        log("debug: setting index %d to %s" % (idx, value))
        if (idx >= self.__length) or (idx + self.__length < 0):
            raise IndexError("%d doesn't exist, length is %d" % (idx, self.__length))

        return self.__properties[idx]



    def __getitem__(self, idx):

        if self.__length <= 0:

            log("Warning: Control not initialized as an array.")
            raise IndexError

        log("debug: getting index %d" % (idx,))
        if (idx >= self.__length) or (idx + self.__length < 0):
            raise IndexError("%d doesn't exist, length is %d" % (idx, self.__length))

        return self.__properties[idx]



    def __delitem__(self, idx):

        if idx < self.__length and idx >= 1:

            # As long as we delete the same index of __control, there will be
            # no property that uses that Control
            del self.__dict__["_ControlWrapper__properties"][idx]
            new_ctrl_list = self.__dict__["_ControlWrapper__control"](open)
            del new_ctrl_list[idx]
            del self.__dict__["_ControlWrapper__control"]
            self.__dict__["_ControlWrapper__control"] = Vault( new_ctrl_list )
            self.__dict__["_ControlWrapper__length"] = self.__length - 1

        else:

            log("Warning: Trying to delete index %d when length is %d." % (idx, self.__length))



    def get_interfaces_id(self):

        """
        @return : implemented interfaces' id
        @rtype : list of str
        """

        return self.__ifaces_id(open)

