from shell.Plugin import Plugin
from utils.Observable import Observable
from utils.Trie import Trie
from main import DISPLAYPATHS
from main.MetaData import MetaData
from utils.QueryParser import QueryParser
from utils.Struct import Struct

import os


#
# Plugin for the collection of installed displays.
#
class Core_DisplayCollection(Plugin, Observable):

    OBS_RELOAD = 0

    def init(self):
        self.__trie = None
        self.__queryparser = None

        self.reload()


    def __find_displays(self, path):

        files = os.listdir(path)
        for f in files:
            filepath = os.path.join(path, f)
            if (os.path.isdir(filepath)):
                self.__find_displays(filepath)
            else:
                name, ext = os.path.splitext(f)
                if (ext == ".display"):
                    meta = MetaData(filepath)
                    item = Struct(path = filepath,
                                  name = meta.get(meta.KEY_NAME),
                                  version = meta.get(meta.KEY_VERSION),
                                  author = meta.get(meta.KEY_AUTHOR),
                                  description = meta.get(meta.KEY_DESCRIPTION),
                                  category = meta.get(meta.KEY_CATEGORY).lower(),
                                  preview = meta.get(meta.KEY_PREVIEW))

                    self.__insert_into_trie(item)
        #end for


    def __insert_into_trie(self, item):

        self.__trie.insert(["name"] + list(item.name), item)
        self.__trie.insert(["path"] + list(item.path), item)
        self.__trie.insert(["author"] + list(item.author), item)
        self.__trie.insert(["version"] + list(item.version), item)
        self.__trie.insert(["description"] + list(item.description),
                           item)
        for c in item.category.split(","):
            self.__trie.insert(["category"] + list(c.strip()), item)


    def add_observer(self, obs):

        def f(src, cmd): obs()
        Observable.add_observer(self, f)
        

    def query(self, query):

        matches = self.__queryparser.parse(query)
        return matches


    def remove(self, item):

        self.__trie.remove(item)
        self.update_observer(self.OBS_RELOAD)


    def reload(self):

        self.__trie = Trie()
        self.__trie.set_case_sensitive(False)
        self.__queryparser = QueryParser(self.__trie)

        # read the display files
        for path in DISPLAYPATHS:
            if (os.path.isdir(path)):
                self.__find_displays(path)
        self.update_observer(self.OBS_RELOAD)
        

def get_class(): return Core_DisplayCollection
