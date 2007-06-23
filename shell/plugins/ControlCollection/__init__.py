from shell.Plugin import Plugin
from main import CONTROLPATHS
from plugin.PluginRegistry import PluginRegistry


#
# Plugin for the collection of installed controls.
#
class Core_ControlCollection(Plugin):

    def init(self):
        self.__registry = PluginRegistry(*CONTROLPATHS)


    def query(self, query):

        matches = self.__registry.get_plugins(query)
        return matches


def get_class(): return Core_ControlCollection
