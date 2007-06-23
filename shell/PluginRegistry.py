from plugin.PluginRegistry import PluginRegistry
from main import HOME, USERHOME

import os


#
# Registry for shell plugins.
#
class _PluginRegistry:

    def __init__(self):

        # prevent from recursion
        self.__cache = {}
        
        # table: query -> result
        self.__query_cache = {}

        path = os.path.dirname(__file__)
        self.__registry = PluginRegistry(os.path.join(path, "plugins"))



    def get_plugins_by_pattern(self, key, pattern):

        query = "(MATCH '%s' '%s')" % (key, pattern)
        if (not query in self.__query_cache):
            result = self.__registry.get_plugins(query)
            self.__query_cache[query] = result[:]
        else:
            result = self.__query_cache[query]

        ret = []

        for c in result:

            if c not in self.__cache:
                self.__cache[c] = c()
                self.__cache[c].init()

            ret.append( self.__cache[c] )

        return ret


    #
    # Returns a control providing the given interfaces.
    #
    def get_plugin(self, name, *interfaces):

        result = self.get_plugins_by_pattern("name", name)
        if (result):
            return result[0]


# singleton object
registry = _PluginRegistry()
