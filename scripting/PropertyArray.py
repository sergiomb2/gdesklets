from Vault import Vault

class PropertyArray():

    # like Vault...open isn't available from the sandbox

    def __init__(self, prop, ctrl, length, key = open):

        self.__dict__["_PropertyArray__key"] = Vault(key)
        self.__dict__["_PropertyArray__property"] = Vault([ prop for i in range(length) ])
        self.__dict__["_PropertyArray__original_property"] = Vault(prop)
        self.__dict__["_PropertyArray__length"] = Vault(length)
        #self.__dict__["_PropertyArray__control"] = ctrl # already locked in Vault
        self._set_control(ctrl, open)



    def __len__(self):

        return self.__length(open)



    def _set_control(self, new_ctrl, k):

        if k != self.__key(open):
            raise RuntimeError("Intrusion detected (in PropertyArray %s)" % self)

        self.__dict__["_PropertyArray__control"] = new_ctrl # already locked in Vault



    def _set_length(self, value, k):

        if k != self.__key(open):
            raise RuntimeError("Intrusion detected (in PropertyArray %s)" % self)

        length = self.__length(open)
        if value <= 0:
            log("Warning: Value of property \"length\" must be greater than 0 (setting to 1)")
            value = 1

        if value != length:
            #print "debug: old length: %d" % length
            #print "debug: new length: %d" % value
            if value > length:
                self.__dict__["_PropertyArray__property"] = \
                    Vault( self.__property(open) + \
                           [ self.__original_property(open)
                             for i in range(length, value) ] )
                #print "debug: added items %s to PropertyArray" % range(length, value)
            elif value < length:
                # We want to leave the 0th item alone
                # This is checked by the above conditionals
                start_deleting_at = value

                prop = self.__property(open)
                for i in range(start_deleting_at, length):
                    #print "debug: deleting item %d" % i
                    del prop[i]
                self.__dict__["_PropertyArray__property"] = Vault(prop)

            self.__dict__["_PropertyArray__length"] = Vault(value)



    def __setitem__(self, key, value):

        if key < 0:
            key = self.__length(open) + key
        if key >= self.__length(open):
            raise IndexError

        try:
            prop = self.__property(open)[key]
        except KeyError:
            log("Warning: Property isn't available at index %d." % (key,))
            raise KeyError

        prop.fset(self.__control(open)[key], value)



    def __getitem__(self, key):

        if key < 0:
            key = self.__length(open) + key
        if key >= self.__length(open):
            raise IndexError

        try:
            prop = self.__property(open)[key]
        except KeyError:
            log("Warning: Property isn't available at index %d." % (key,))
            return None

        return prop.fget(self.__control(open)[key])
