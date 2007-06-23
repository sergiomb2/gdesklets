from sensor.Sensor import Sensor

import commands
import time


#
# Sensor for invoking external programs.
#
class External(Sensor):

    def __init__(self, cmd, interval = 1000):

        self.__output = ""


        Sensor.__init__(self)
        self._add_timer(100, self.__on_tick, int(interval))
        if (int(interval) > 0):
            self._add_thread(self.__command_thread, cmd,
                             0.001 * float(interval))
        else:
            fail, output = commands.getstatusoutput(cmd)
            if (fail): output = ""
            self.__output = output



    def __on_tick(self, interval):

        data = self._new_output()
        if (self.__output): data.set("value", self.__output)
        self._send_output(data)

        if (interval > 0): self._add_timer(interval, self.__on_tick, interval)



    def __command_thread(self, cmd, interval):

        while not self._is_stopped():

            fail, output = commands.getstatusoutput(cmd)
            if (fail): output = ""

            self.__output = output
            time.sleep(interval)


def new_sensor(args): return External(*args)
