from main import REGISTRY_PATH

import os
import random
from Backend import Backend
import shutil
import threading
import string


class StateSaverServer(object):
    """
      This class provides a singleton server object for saving program state
      in a database. The path of the database file contains random elements in
      order to not be attackable by "known-location attacks".
    """

    __STATES_FILE = os.path.join(REGISTRY_PATH,
              "states" + hex(random.randrange(0xffffffL, 0xffffffffL)) + ".db")
    __CONFIG_FILE = os.path.join(REGISTRY_PATH,
              "config" + hex(random.randrange(0xffffffL, 0xffffffffL)) + ".db")
    __SEPARATOR = ' '
    

    def __init__(self):

        self.__lock = threading.Lock()

        self.__db_file = self.__find_db()
        self.__db = Backend(self.__db_file)
        if (os.path.basename(self.__db_file).startswith("states")):
            self.__db.set_file(self.__CONFIG_FILE)
            
        self.__dirty = False

        # flush the cache every 5 seconds
        import gobject
        gobject.timeout_add(5 * 1000, self.__flush)



    def __flush(self):

        if (self.__dirty):
            self.__db.sync()
            self.__dirty = False
        return True



    def __find_db(self):

        files = os.listdir(REGISTRY_PATH)
        legacy_dbs = [ f for f in files if f.startswith("states") ]
        dbs = [ f for f in files if f.startswith("config") ]

        if (dbs):
            pos = dbs[-1].find(".db")
            return os.path.join(REGISTRY_PATH, dbs[-1][0:pos+3])
        elif (legacy_dbs):
            pos = legacy_dbs[-1].find(".db")
            return os.path.join(REGISTRY_PATH, legacy_dbs[-1][0:pos+3])
        else:
            return self.__CONFIG_FILE



    def __check_key(self, key):

        assert key
        assert key[0] not in string.digits

        for c in key:
            assert c in (string.ascii_letters + string.digits + '-_.[]')



    def set_key(self, ident, key, value):

        self.__check_key(key)

        self.__lock.acquire()

        try:
            pk = ident + self.__SEPARATOR + key
            self.__db[pk] = value
            self.__dirty = True
        finally:
            self.__lock.release()



    def get_key(self, ident, key, default):

        self.__check_key(key)

        self.__lock.acquire()

        try:
            pk = ident + self.__SEPARATOR + key
            return self.__db.get(pk, default)
        finally:
            self.__lock.release()



    def remove(self, ident):

        self.__lock.acquire()

        try:
            self.__dirty = True
            for k in self.__db.keys():
                if k.startswith(ident + self.__SEPARATOR):
                    del self.__db[k]
        finally:
            self.__lock.release()



    def list(self, ident):

        self.__db.sync()
        return [k[len(ident) + 1:] for k in self.__db.keys() \
                if k.startswith(ident + self.__SEPARATOR)]


_SERVER = StateSaverServer()



class StateSaverClient(object):

    __slots__ = "__ident",

    def __init__(self, ident):
        self.__ident = ident

    def set_key(self, key, value):
        _SERVER.set_key(self.__ident, key, value)

    def get_key(self, key, default = None):
        return _SERVER.get_key(self.__ident, key, default)

    def remove(self):
        _SERVER.remove(self.__ident)

    def list(self):
        return _SERVER.list(self.__ident)


StateSaver = StateSaverClient

_singleton = StateSaver("__default__")
def DefaultStateSaver(): return _singleton
