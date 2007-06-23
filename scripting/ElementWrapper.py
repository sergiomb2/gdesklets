from Vault import Vault


class ElementWrapper(object):
    """
      The ElementWrapper wraps Element objects for use in the sandbox.
      By wrapping it up, there remains no way to access the internals of the
      element. Only the properties and authorized methods will be available.
    """

    def __init__(self, target):

        self.__dict__["_ElementWrapper__target"] = Vault(target)


    def __setattr__(self, name, value):

        self.__target(open).set_prop(name, value)


    def __getattr__(self, name):

        if name in self.__target(open).AUTHORIZED_METHODS:
            return getattr(self.__target(open), name)

        return self.__target(open).get_prop(name)
