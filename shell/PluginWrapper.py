class PluginWrapper(object):

    def __init__(self, plugin, methods):

        self.__methods = methods
        self.__plugin = plugin
            


    def __getattr__(self, key):

        methods = self.__methods
        plugin = self.__plugin
        if (key in methods):
            return getattr(plugin, key)
        else:
            raise KeyError("No such method: %s" % (key))
