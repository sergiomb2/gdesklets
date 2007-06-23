from factory.SensorFactory import SensorFactory
from main.Control import Control
from ISensor import ISensor

import gtk


#
# This control wraps legacy sensors to make them still usable.
# Sensors are deprecated and shouldn't be used in new stuff. This control is
# solely meant for retaining backwards compatibility.
#
class Sensor(Control, ISensor):

    def __init__(self):

        self.__sensor = None
        self.__sensor_factory = SensorFactory()

        self.__output = None
        self.__menu = None


        Control.__init__(self)


    #
    # Loads the given sensor with arguments.
    #
    def __set_sensor(self, value):

        module, args = value
        sensor = self.__sensor_factory.create_sensor(module, args)
        if (sensor):
            sensor.add_observer(self.__on_observe_sensor)
        else:
            raise RuntimeError("Could not load sensor")

        self.__sensor = sensor


    #
    # Sends an action to the sensor.
    #
    def __set_action(self, value):

        callname, path, allargs = value
        self.__sensor.send_action(callname, path, allargs)

    def __set_config_id(self, value): self.__sensor.set_config_id(value)

    def __set_stop(self, value): self.__sensor.stop()

    def __get_output(self): return self.__output
    def __get_menu(self): return self.__menu
    def __get_configurator(self): return self.__sensor.get_configurator()


    #
    # Observer for the sensor.
    #
    def __on_observe_sensor(self, src, cmd, data):

        # propagate the incoming sensor output
        if (cmd == src.OBS_OUTPUT):
            self.__output = data
            self._update("output")

        elif (cmd == src.OBS_CMD_MENU):
            self.__menu = data
            self._update("menu")


    sensor = property(None, __set_sensor, doc = "the sensor")
    action = property(None, __set_action, doc = "the action to perform")
    config_id = property(None, __set_config_id, doc = "the config ID")
    stop = property(None, __set_stop, doc = "stops the sensor")
    output = property(__get_output, None,
                      doc = "the output data of the sensor")
    menu = property(__get_menu, None,
                      doc = "the menu data of the sensor")
    configurator = property(__get_configurator, None,
                            doc = "the configurator of the sensor")


def get_class(): return Sensor
