from utils.Element import Element
from utils.Observable import Observable
from utils.datatypes import *
from utils import actionparser


#
# Abstract class for data targets.
#
class DataTarget(Element, Observable):

    __slots__ = ('__actions', '__index_path', '__parent', '__display',
    '__watch_bindings', '__index')

    AUTHORIZED_METHODS = ()

    def __init__(self, name, parent):

        # the actions and their associated calls
        self.__actions = {}

        # the index path of this target
        self.__index_path = []

        # the parent of this target
        self.__parent = parent

        # the display of this target
        self.__display = parent._get_display()

        # list of watch bindings for being able to unbind the sensor again
        # FIXME: remove eventually :)
        self.__watch_bindings = []

        Element.__init__(self, name)

        self._register_property("event", TYPE_OBJECT, None, self._getp)
        self._register_property("index-path", TYPE_INT, None, self._getp)
        self._register_property("watch", TYPE_LIST, self._setp_watch, None)

        if (parent and not self.is_standalone()):
            self.__index = parent.get_next_child_index()
            self.__index_path = parent.get_index_path()
        else:
            self.__index = -1
            self.__index_path = []

        if (not self.is_standalone()):
            self.add_observer(parent.child_observer)

        if (self.__index != -1): self.__index_path.append(self.__index)
        if (self.__index_path):
            self._setp("index-path", self.__index_path[:])
        else:
            self._setp("index", [])



    #
    # Returns the parent of this target.
    #
    def _get_parent(self): return self.__parent



    #
    # Returns whether this target is standalone, i.e. needs no parent.
    #
    def is_standalone(self): return True



    #
    # Tells this target about its XML name.
    #
    def set_name(self, name): self.__name = name


    def delete(self):

        self.drop_observers()
        self.__unbind_sensors()



    #
    # Returns the display of this target.
    #
    def _get_display(self): return self.__display



    #
    # Returns the sensor watch propagator of this target. This is either the
    # display window or an array.
    #
    def _get_propagator(self):

        parent = self._get_parent()
        while (parent and not parent.__class__.__name__ == "TargetArray"):
            parent = parent._get_parent()

        if (not parent): parent = self._get_display()

        return parent



    #
    # Returns the index path of this target.
    #
    def get_index_path(self): return self.__index_path[:]



    #
    # Registers the given action.
    #
    def _register_action(self, action):

        self._register_property("on-" + action, TYPE_STRING,
                                self._setp__action, self._getp)



    #
    # Sets the given XML property. This is the same as set_prop() but takes
    # strings as values and converts before setting.
    #
    def set_xml_prop(self, key, value):

        self.set_prop_from_string(key, value)



    #
    # Emits the given action if the pointer is over this target.
    #
    def get_action_call(self, action):

        return self.__actions.get(action, None)



    #
    # Handles the given action.
    #
    def handle_action(self, action, px, py, event):

        call = self.get_action_call(action)
        if (call):
            # analyze call to see if it's a legacy call
            # FIXME: remove eventually :)
            import re
            if (re.match("[\w\-]+:.*", call)):
                log("Deprecation: Please use new style call.",
                    is_warning = True)

                try:
                    legacy_args = event._args
                except:
                    legacy_args = []

                legacy_call = actionparser.parse(call)
                path = self.get_index_path()
                self._get_display().call_sensor(legacy_call, path,
                                                *legacy_args)

            else:
                self._setp("event", event)
                self._get_display().execute_callback_script(call, self)


    #
    # Unbinds this target from the sensors.
    # FIXME: remove eventually :)
    #
    def __unbind_sensors(self):

        for sensorplug, prop in self.__watch_bindings:
            self._get_display().unbind_sensor(sensorplug, self, prop)
        #end for
        self.__watch_bindings = []



    #
    # Action handlers.
    #
    def _setp__action(self, key, value):

        name = key[3:]
        self.__actions[name] = value
        self._setp(key, value)



    #
    # "watch" property.
    #
    def _setp_watch(self, key, value):

        entries = value
        for e in entries:
            prop, sensorplug = e.split("=")
            if (self.__index_path):
                self._get_display().register_array_for_port(
                    self._get_propagator(),
                    sensorplug)
                sensorplug += str(self.__index_path)
            self._get_display().bind_sensor(sensorplug, self, prop)
            self.__watch_bindings.append((sensorplug, prop))

