class PropertyArray():

    def __init__(self, prop, ctrl, length):

        self.__dict__["_PropertyArray__property"] = Vault([ prop for i in range(length) ])
        self.__dict__["_PropertyArray__control"] = ctrl # already locked in Vault
        self.__dict__["_PropertyArray__length"] = Vault(length)



    def __len__(self):

        return self.__dict__["_PropertyArray__length"](open)



    def __setitem__(self, key, value):

        try:
            prop = self.__property(open)[key]
        except KeyError:
            log("Warning: Property isn't available at index %d." % (key,))
            raise KeyError

        prop.fset(self.__control(open)[key], value)



    def __getitem__(self, key):

        if key <= (0 - self.__length(open)) or key >= self.__length(open):
            raise IndexError

        try:
            prop = self.__property(open)[key]
        except KeyError:
            log("Warning: Property isn't available at index %d." % (key,))
            return None

        return prop.fget(self.__control(open)[key])


    def __delitem__(self, key):

        if key <= (0 - self.__length(open)) or key >= self.__length(open):
            raise IndexError

        prop = self.__property(open)
        length = self.__length(open)

        try:
            del prop[key]
        except KeyError:
            log("Warning: Property isn't available at index %d." % (key,))
            raise KeyError

        length -= 1

        self.__property = Vault(prop)
        self.__length = Vault(length)
