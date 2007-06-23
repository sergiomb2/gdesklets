import gtop
from Device import Device

import time
import threading

class Net(Device):

    """Provides storage for interface statistics in order to poll
    multiple network devices at the same time"""

    def __init__(self, dev):

        Device.__init__(self)

        self.__dev = dev
        buf = gtop.netload(dev)
        self.__in, self.__out = buf.bytes_in, buf.bytes_out
        self.__time = time.time()
        self.__lock = threading.Lock()


    def poll(self):

        """Returns .
        self.poll() is threadsafe"""

        self.__lock.acquire()
        try:
            buf = gtop.netload(self.__dev)
            bytes_in, bytes_out = buf.bytes_in, buf.bytes_out

            now      = time.time()
            interval = now - self.__time

            in_diff  = bytes_in  - self.__in
            out_diff = bytes_out - self.__out

            speed_in  = int(in_diff / interval)
            speed_out = int(out_diff / interval)

            self.__time = now
            self.__in, self.__out = bytes_in, bytes_out

            return (speed_in, speed_out)

        finally:
            self.__lock.release()
