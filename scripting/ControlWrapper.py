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
        if size <= 0:
            size = 1

        # We need to deepcopy in order to get individually changeable
        # Control instances
        try:
            self.__dict__["_ControlWrapper__control"] = \
                         Vault( [ deepcopy(control)
                                  for i in range(size) ] )
        except:
            self.__dict__["_ControlWrapper__control"] = \
                         Vault( [ control ] )
            if self.__length > 0:
                log(_("Error: Control %s can't be replicated! This is a BUG in the Desklet!"
                      "\nThings probably won't work right for you.") % control)
                self.__dict__["_ControlWrapper__length"] = 0
                size = 1
        else:
            # Initialize all initial copies
            for ctl in self.__dict__["_ControlWrapper__control"](open):
                ctl.__init__()

        # Keep an original copy around for extending the array
        self.__dict__["_ControlWrapper__original_control"] = Vault(control)
        # deactivate the original control
        ctl = self.__dict__["_ControlWrapper__original_control"](open)
        ctl.stop()
        # Create a property handler for each deep copy of control
        self.__dict__["_ControlWrapper__properties"] = \
                     [ PropertyInterface(self.__control(open)[i])
                       for i in range(size) ]

        ids =  [ Interface.get_id(i)
                 for i in Interface.get_interfaces( control.__class__ ) ]
        taz_ids = [ Interface.get_taz_style_id(i)
                    for i in Interface.get_interfaces( control.__class__ ) ]

        self.__dict__["_ControlWrapper__ifaces_id"] = \
                                                  Vault( tuple(ids + taz_ids) )


    def __len__(self):

        return self.__length



    def __setattr__(self, name, value):

        if self.__length > 0:

            if name == "length":
                # A little bounds checking
                size = value
                if value < 0:
                  value = 0
                  log(_("Warning: Value of property \"length\" must be greater than or equal to 0 (setting to 0)"))
                if value == 0:
                  log(_("Warning: Value of property \"length\" set to 0 disables list mode"))
                  size = 1

                # Don't do anything if value isn't changing
                if size != self.__length:
                    if size > self.__length:
                        # Append new copies of the control
                        self.__dict__["_ControlWrapper__control"] = \
                            Vault( self.__control(open) +           \
                                   [ deepcopy(self.__original_control(open))    \
                                     for i in range(self.__length, size) ] )
                        # Initialize all new copies of the control
                        for ctl in [ self.__dict__["_ControlWrapper__control"](open)[i] \
                                     for i in range(self.__length, size) ]:
                            ctl.__init__()
                        # Append new PropertyInterface instances
                        self.__dict__["_ControlWrapper__properties"] = \
                            self.__properties +                        \
                            [ PropertyInterface(self.__control(open)[i])    \
                              for i in range(self.__length, size) ]
                    elif size < self.__length:
                        # We want to leave the "0th" item alone, which is 
                        # handled by the above conditionals
                        for i in range(size, self.__length):
                            del self[size]

                    self.__dict__["_ControlWrapper__length"] = value
            else: # name != "length"
                # This is the case where someone tries to set a property
                # of this class when the length != 0. They should know
                # better if they've gone and changed the length, but we'll
                # be nice and print out some informational warnings.
                log(_("Warning: Property \"%s\" must be indexed (length == %d).") % (name, self.__length))
                return

        else: # length <= 0

            # Backwards compatibility
            self.__dict__["_ControlWrapper__properties"][0].__setattr__(name, value)



    def __getattr__(self, name):

        if name in Control.AUTHORIZED_METHODS:
            if self.__length <= 0:
                return getattr(self.__control(open)[0], name)
            else:
                return self.__control(open)

        if self.__length <= 0:
            # Backwards compatibility
            return self.__dict__["_ControlWrapper__properties"][0].__getattr__(name)
        elif name == "length":
            return self.__length
        else:
            # This is the case where someone tries to set a property
            # of this class when the length != 0.  They should know
            # better if they've gone and changed the length, but we'll
            # be nice and print out some informational warnings.
            log(_("Warning: Property \"%s\" must be indexed (length == %d).") % (name, self.__length))
            return



    def __setitem__(self, idx, value):

        if self.__length <= 0:

            log(_("Warning: Control not initialized as an array in Desklet."))
            raise IndexError

        if (idx >= self.__length) or (idx + self.__length < 0):
            raise IndexError("%d doesn't exist, length is %d" % (idx, self.__length))

        return self.__properties[idx]



    def __getitem__(self, idx):

        if self.__length <= 0:

            log(_("Warning: Control not initialized as an array in Desklet."))
            raise IndexError

        if (idx >= self.__length) or (idx + self.__length < 0):
            raise IndexError("%d doesn't exist, length is %d" % (idx, self.__length))

        return self.__properties[idx]



    def __delitem__(self, idx):

        if self.__length > 0:

            if idx < 0:
                idx = self.__length + idx

            if idx < self.__length and idx >= 0:

                # As long as we delete the same index of __control, there will be
                # no property that uses that Control
                del self.__dict__["_ControlWrapper__properties"][idx]
                new_ctrl_list = self.__dict__["_ControlWrapper__control"](open)
                new_ctrl_list[idx].stop()
                del new_ctrl_list[idx]
                #del self.__dict__["_ControlWrapper__control"]
                self.__dict__["_ControlWrapper__control"] = Vault( new_ctrl_list )
                self.__dict__["_ControlWrapper__length"] -= 1

            else:

                log(_("Warning: Trying to delete index %d when length is %d.") % (idx, self.__length))

        else:

            log(_("Warning: Control not initialized as an array in Desklet; not deleting anything."))

    def stop(self):

        for c in self.__dict__["_ControlWrapper__control"](open):
            try:
                c.stop()
            except StandardError, exc:
                import traceback; traceback.print_exc()
                log("Could not stop control %s" % c)
            del c

        # original control is already stopped
        c = self.__dict__["_ControlWrapper__original_control"](open)
        del c




    def get_interfaces_id(self):

        """
        @return : implemented interfaces' id
        @rtype : list of str
        """

        return self.__ifaces_id(open)

