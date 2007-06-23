#from config.StateSaver import DefaultStateSaver


#
# Abstract base class for plugins.
#
class Plugin(object):

    def init(self): pass


    def _get_path(self): return self._path


    def _get_plugins_by_pattern(self, key, pattern):

        from PluginRegistry import registry
        return registry.get_plugins_by_pattern(key, pattern)


    def _get_plugin(self, name, *interfaces):

        from PluginRegistry import registry
        plugin = registry.get_plugin(name, *interfaces)
        if (not plugin):
            print "Plugin not found:", name

        return plugin


    def _set_config(self, key, value):

        #backend = DefaultStateSaver()
        #backend.set_key(key, value)
        pass


    def _get_config(self, key):

        #backend = DefaultStateSaver()
        #return backend.get_key(key, True)
        return True
