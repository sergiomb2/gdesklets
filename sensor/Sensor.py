#:section Sensor
#
#:  para The [cmd:Sensor] class is an abstract base class where new sensors are
#        derived from. This class takes care of communication with the
#        [app:gDesklets] core, so you can fully concentrate on the sensor
#        itself.

from utils.Observable import Observable
from utils.TargetSettings import TargetSettings
from utils import i18n
from utils import MAIN_THREAD
from utils import run_in_main_thread
from config.ConfigManager import ConfigManager
from SensorConfigurator import SensorConfigurator
from main import _
from main import PURGE_KEY

import gobject
import gtk
import thread
import time
import os


#
#:class Sensor |
# Abstract base class for all sensors. Every sensor has to inherit from this
# class.
#
class Sensor(Observable):

    OBS_OUTPUT = 0
    OBS_CMD_CONFIGURE = 1
    OBS_CMD_REMOVE = 2
    OBS_CMD_RESTART = 3
    OBS_CMD_DUPLICATE = 4
    OBS_CMD_MENU = 5


    def __init__(self):

        # the path of this sensor
        self.__path = os.getcwd()

        # configuration manager for sensor properties
        self.__config_manager = ConfigManager()
        self.__config_id = ""

        # the ID of this sensor
        self.__sensor_id = ""

        # the configuration watcher callback
        self.__config_watcher = None

        # flag for stopping the sensor
        self.__stop_flag = False

        # when stopping, the flag is set to True, then the callback is called
        self.__stop_callback = None

        self.__defaults = {}



    #
    # Sets the ID of this sensor.
    #
    def set_id(self, ident):

        self.__id = ident



    #
    #:function get_id | |
    #          Returns the ID of this sensor. It is not yet valid in the
    #          constructor.
    #:  return string
    #:/function
    #
    def get_id(self):
        assert self.__id, "The ID is invalid in the constructor."

        return self.__id



    #
    # Sets the configuration ID for this sensor.
    # If the user has set a callback function for watching the config,
    # the config will be watched.
    #
    def set_config_id(self, config_id):

        self.__config_id = str(config_id)
        if (self.__config_watcher):
            Sensor.watch_config(self, self.__config_watcher)



    #
    #:function get_config_id | |
    #          Returns the unique config ID of the sensor. You can use the ID
    #          if you need to store data in other places.
    #:  return string
    #:/function
    #
    def get_config_id(self):

        return self.__config_id



    #
    #:function set_config | key, value |
    #          Stores the given value in the configuration base.
    #:  param key   | string | The key name.
    #:  param value | string | The value to set.
    #:/function
    #
    def set_config(self, key, value):
        assert(self.__config_manager)

        if (not self.__stop_flag):
            run_in_main_thread(self.__config_manager.set,
                               self.__config_id, key, value)



    #
    #:function get_config | key |
    #          Returns the configuration value for the given key.
    #:  param  key | string | The key name.
    #:  return string
    #:/function
    #
    def get_config(self, key):
        assert(self.__config_manager)

        value = run_in_main_thread(self.__config_manager.get,
                                   self.__config_id, key)

        if (value == self.__config_manager.UNDEF):
            value = self.__defaults.get(key, "")

        return value



    #
    #:function watch_config | callback |
    #          Registers a watcher for config changes.
    #:  param callback | function | The callback function for configuration
    #                               changes.
    #:/function
    #
    def watch_config(self, callback):

        self.__config_watcher = callback
        if (self.get_config_id()):
            self.__config_manager.watch(self.get_config_id(),
                                        self.__on_watch_config)



    #
    #:function _set_config_type | key, type, default |
    #          Sets the data types to be used for the configuration values.
    #          Use this method in the constructor of your sensor.
    #:  param  key | string | The name of the configuration key.
    #:  param  type | enum  | The data type of the configuration key.
    #:  param  default | string | The default value or unset keys.
    #:/function
    #
    def _set_config_type(self, key, dtype, default):

        self.__defaults[key] = default


    #
    #:function get_path | | Returns the filesystem path of the sensor. Use this
    #                       method if you want to load resource files that come
    #                       with the sensor.
    #:  return string
    #:/function
    #
    def get_path(self): return self.__path



    #
    #:function set_path_to_purge | paths |
    #          Sets the paths which are to be removed when the desklet that
    #          uses the sensor gets removed.
    #          If your sensor creates files, you need to specify the paths here
    #          in order to clean up.
    #:  param  paths | string list | The paths to purge.
    #:/function
    #
    def set_paths_to_purge(self, paths):

        key = PURGE_KEY
        value = ",".join(paths)
        self.__config_manager.set(self.__config_id,
                                  key, value)



    #
    #:function new_output || Returns a new empty [cmd:TargetSettings] object for sending data to
    #          the display.
    #:  return TargetSettings
    #:/function
    #
    def new_output(self): return TargetSettings()



    #
    #:function send_output | output | Sends the given [cmd:TargetSettings] object to the display.
    #          [emph:Never call this method from within a thread!]
    #:  param  output | TargetSettings | The object for sending to the display.
    #:/function
    #
    def send_output(self, output):

        run_in_main_thread(self.update_observer, self.OBS_OUTPUT, output)



    #
    #:function add_timer | interval, callback, *args | Adds a timeout function with the given
    #          interval in ms.
    #:  param  interval | int | The timeout interval between each invokation of the callback.
    #:  param  callback | function | The callback function.
    #:/function
    #
    def add_timer(self, interval, callback, *args):

        def __wrap(self, callback, args):
            if (not self.__stop_flag):
                try:
                    return callback(*args)
                except:
                    from utils.error import Error
                    Error().handle("unknown")
                    return False
            else:
                return False

        return gobject.timeout_add(interval, __wrap, self, callback, args)



    #
    #:function add_thread | threadfunction, *args | Adds and runs a new thread.
    #          Use this to start new threads. It's recommended to put blocking actions into threads
    #          in order to not block [app:gDesklets].
    #:  param threadfunction | function | The thread function.
    #:/function
    #
    def add_thread(self, threadfunction, *args):

        # the thread should not start before setup is complete, therefore
        # we are using the GTK idle handler
        def run_thread(threadfunction, args):
            thread.start_new_thread(threadfunction, args)
            return False

        gobject.idle_add(run_thread, threadfunction, args)



    #
    # Sends an action to this sensor.
    #
    def send_action(self, call, path, args = []):

        if (not self.__stop_flag):
            try:
                self.call_action(call, path, args)
            except:
                from utils.error import Error
                Error().handle("unknown")




    #
    #:function call_function | call, path, *args | Method for handling action calls from the
    #          display. Sensors have to override this method. [emph:This method may soon be
    #          deprecated!]
    #:  param  call | string | The function to call.
    #:  param  path | int list | The path of the target on which the action occurred.
    #:  param  args | any list | The list of arguments for the function call.
    #:/function
    #
    def call_action(self, call, path, args = []): raise NotImplementedError



    def watch_stop(self, callback):

        """
        Registers a callback that will be called when sensor will be stopped.

        @param callback:
        @type  callback: callable(callback)
        """

        self.__stop_callback = callback


    #
    # Stops this sensor and cleans up.
    #
    def stop(self):

        self.__stop_flag = True
        if (self.__stop_callback): self.__stop_callback()

        del self.__config_watcher
        self.__config_manager.remove_watcher(self.get_config_id(),
                                             self.__on_watch_config)

        # shut down sensor
        self._shutdown()



    #
    #:function is_stopped | | Returns whether this sensor has been stopped. Use this method to
    #          check if your threads have to terminate.
    #:  return bool
    #:/function
    #
    def is_stopped(self): return self.__stop_flag



    #
    #:function _shutdown | | Executes tasks for sensor shutdown. Override this method if your
    #          sensor has to clean up things after it has been terminated.
    #:/function
    #
    def _shutdown(self): pass



    #
    #:function _new_configurator | | Creates and returns an empty new sensor configurator.
    #          [emph:This method may soon be deprecated!]
    #:  return SensorConfigurator.
    #:/function
    #
    def _new_configurator(self): return SensorConfigurator(self.set_config,
                                                           self.get_config)


    #
    # Returns the configurator of this sensor.
    #
    def get_configurator(self): pass



    #
    # Method for duplicating the display using this sensor
    #
    def _duplicate_display(self):

        self.update_observer(self.OBS_CMD_DUPLICATE)



    #
    #:function open_menu | menu | Opens the given popup menu. The menu is a list of
    #          [cmd:(label:str, sensitive:bool, submenu:list, callback:function, args: list)]
    #          tuples.
    #:  param  menu | list | The menu to open.
    #:/function
    #
    def open_menu(self, menu):

        menu += [()]
        run_in_main_thread(self.update_observer, self.OBS_CMD_MENU, menu)



    #
    # Reacts on changes in the configuration and delegates the call to the
    # user's callback.
    #
    def __on_watch_config(self, path, value):
        assert(self.__config_watcher)

        key = path[-1]
        self.__config_watcher(key, value)



    def __on_configure(self, src):

        self.update_observer(self.OBS_CMD_CONFIGURE, None)



    def __on_remove(self, src):

        self.update_observer(self.OBS_CMD_REMOVE, None)



    def __on_restart(self, src):

        self.update_observer(self.OBS_CMD_RESTART, None)



    # some required aliases for older sensors to work
    _get_id = get_id
    _get_path = get_path
    _new_output = new_output
    _send_output = send_output
    _add_timer = add_timer
    _add_thread = add_thread
    _is_stopped = is_stopped
    _get_config_id = get_config_id
    _watch_config = watch_config
    _set_config = set_config
    _get_config = get_config
    _set_paths_to_purge = set_paths_to_purge
    _open_menu = open_menu

