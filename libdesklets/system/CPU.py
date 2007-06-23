import gtop
from Device import Device

import threading


class Total(Device):

    def __init__(self):

        Device.__init__(self)

        self.__total = 0.0
        self.__user  = 0.0
        self.__sys   = 0.0
        self.__nice  = 0.0
        self.__idle  = 0.0
        self.__lock  = threading.Lock()



    def _get_cpu(self): return gtop.cpu()


    def poll(self):

        """
        @return : cpu load
        @rtype  : float
        """
        self.__lock.acquire()

        try:
            cpu = self._get_cpu()
            totaldiff = cpu.total - self.__total
            load = float(cpu.frequency * ((cpu.user + cpu.sys + cpu.nice) -
                                          (self.__user + self.__sys + self.__nice))
                         / (totaldiff + 0.001) + 0.5)

            if (load > 100.0): load = 100.0

            self.__total = cpu.total
            self.__user  = cpu.user
            self.__sys   = cpu.sys
            self.__nice  = cpu.nice
            self.__idle  = cpu.idle

            return load

        finally:
            self.__lock.release()




class CPU(Total):

    def __init__(self, n):

        Total.__init__(self)
        self.__n = n


    def _get_cpu(self): return gtop.cpu().cpus[self.__n]
