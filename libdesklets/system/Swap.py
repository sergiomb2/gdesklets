from Device import Device

import threading
import time

class Swap(Device):

    def __init__(self):

        Device.__init__(self)

        self.__pagein  = 0
        self.__pageout = 0
        self.__time    = time.time()
        self.__lock    = threading.Lock()


    def poll(self):

        self.__lock.acquire()

        try:
            swap = gtop.swap()

            now       = time.time()
            page_in   = swap.pagein
            page_out  = swap.pageout

            time_diff = now - self.__time
            in_diff   = pagein  - self.__pagein
            out_diff  = pageout - self.__pageout

            speed_in  = int(in_diff / time_diff)
            speed_out = int(out_diff / time_diff)

            self.__pagein = page_in
            self.__pageout = page_out
            self.__time = now

            return (speed_in, speed_out)

        finally:
            self.__lock.release()

