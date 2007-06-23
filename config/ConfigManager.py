from StateSaver import StateSaver
from utils.Observable import Observable
import utils


class _ConfigManager(Observable):
    """
    This class acts as a compatibility adaptor for deprecated sensors and can
    be removed as soon as support for sensors is being dropped.
    """

    UNDEF = "-- undef --"

    OBS_UPDATE = 1
    

    def __init__(self):

        self.__db = StateSaver("sensors")

        # hashtable for config change handlers: path -> handler
        self.__handlers = {}

        self.add_observer(self.__on_observe_backend)



    def __on_observe_backend(self, src, cmd, *args):

        if (cmd == src.OBS_UPDATE):
            path, value = args

            parts = path.split(".")
            for i in range(len(parts)):
                handler = self.__handlers.get(tuple(parts[:i + 1]))
            
                if (handler):
                    handler(parts, value)
                    break
            #end for



    def watch(self, *args):

        """Sets a callback handler for watching changes for the given
        configuration entry."""

        path = args[:-1]
        print "ADD WATCH", path
        handler = args[-1]
        self.__handlers[path] = handler



    def remove_watcher(self, *args):

        """Removes a watch callback handler."""

        try:
            path = args[:-1]
            del self.__handlers[path]
        except KeyError:
            pass


    def set(self, *args):

        path = ".".join(args[:-1])
        value = args[-1]

        self.__db.set_key(path, value)
        utils.request_call(self.update_observer, self.OBS_UPDATE, path, value)



    def get(self, *args):

        path = ".".join(args)
        value = self.__db.get_key(path, self.UNDEF)

        return value




_singleton = _ConfigManager()
def ConfigManager(): return _singleton
