from utils.Trie import Trie
from utils.QueryParser import QueryParser
from plugin.Interface import Interface
from main import HOME

import os
import sys


if "." not in sys.path: sys.path.append(".")
if HOME not in sys.path: sys.path.append(HOME)


#
# Registry class for finding and indexing plugins.
#
class PluginRegistry:

    # the keys for indexing plugins
    INTERFACE = "interface"
    TAZINTERFACE = "tazinterface"
    NAME = "name"
    MTIME = "mtime"


    def __init__(self, *repositories):

        # the trie for indexing the registered plugins
        self.__trie = Trie()

        # the query parser that is wrapped around the trie
        self.__queryparser = QueryParser(self.__trie)

        for repo in repositories:
            self.__scan_repository(repo)



    #
    # Scans the given repository for plugins and registers them.
    #
    def __scan_repository(self, repo):

        if (os.path.exists(repo)): files = os.listdir(repo)
        else: return

        for f in files:
            pluginpath = os.path.join(repo, f)
            if (os.path.exists(os.path.join(pluginpath, "__init__.py"))):
                cwd = os.getcwd()

                try:
                    os.chdir(repo)
                except OSError, exc:
                    print >> sys.stderr, "Couldn't chdir to %s" % (repo,)

                try:
                    module = __import__(f)
                    self.__register_plugin(module)
                except StandardError, exc:
                    print >> sys.stderr, "%s\n%s in %s is NOT a valid plugin!" \
                                         % (exc, f, pluginpath)

                os.chdir(cwd)

            elif (os.path.isdir(pluginpath)): self.__scan_repository(pluginpath)



    def __register_plugin(self, module):

        clss = module.get_class()
        path = os.path.abspath(os.path.dirname(module.__file__))
        clss._path = path
        interfaces = Interface.get_interfaces(clss)
        name = clss.__name__
        mtime = os.path.getmtime(module.__file__)

        self.__trie.insert([self.NAME] + list(name), clss)
        self.__trie.insert([self.MTIME] + list(`mtime`), clss)

        for iface in interfaces:
            ident = Interface.get_id(iface)
            taz_ident = Interface.get_taz_style_id(iface)
            self.__trie.insert([self.INTERFACE] + list(ident), clss)
            self.__trie.insert([self.TAZINTERFACE] + list(taz_ident), clss)


    def get_plugins(self, query):

        return self.__queryparser.parse(query)

