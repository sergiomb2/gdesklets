import os
import gtop

import CPU
import Net
import Swap


class Arch:

    def __init__(self):

        self.__initialised = False

        self.__cpu_total = CPU.Total()

        self.__cpu_cpus  = [ CPU.CPU(i) for i in range(len(gtop.cpu().cpus)) ]

        self.__net_devices = {}

        self.__swap = Swap.Swap()

        self.__os, self.__name, self.__kernel = os.uname()[:3]


    def _init(self):

        if (self.__initialised):
            return
        else:
            self.__initialised = True
            self.__net_devices = dict( [ (iface, Net.Net(iface))
                                         for iface in self.net_devices() ] )



    def kernel_version(self):
        """
        @return : kernel which is currently running
        @rtype  : str
        """

        return self.__kernel


    def hostname(self):
        """
        @return : the machine's name
        @rtype  : str
        """

        return self.__name


    def operating_system(self):
        """
        @return : operating system which is currently running
        @rtype  : str
        """

        return self.__os


    def net_speed(self, dev):
        """
        @param dev: interface
        @type  dev: str

        @return : (speed in, speed out)
        @rtype  : tuple
        """

        try:
            value = self.__net_devices[dev].poll()
        except KeyError:
            log("Info:\n"
                "%s doesn't exist! Falling back to \"lo\"." % (dev,))
            value = self.__net_devices["lo"].poll()
        return value


    def net_state(self, dev):
        """
        @param dev: interface
        @type  dev: str

        @return : whether a network device is up or not (i.e. down)
        @rtype  : bool
        """

        return gtop.netload(dev).if_flags & gtop.NETLOAD_IF_FLAGS_UP


    def users(self):
        """
        @return : number of users.
        @rtype  : int
        """

        return len(os.popen("users").read().split())


    def cpu_load(self):
        """
        @return : cpu load
        @rtype  : float
        """

        return self.__cpu_total.poll()


    def cpu_count(self):
        """
        @return : number of installed CPUs
        @rtype  : int
        """

        return len(self.__cpu_cpus)


    def all_cpu_load(self):
        """
        @return : total load of installed CPUs
        @rtype  : list
        """

        return [ cpu.poll() for cpu in self.__cpu_cpus ]


    def swap_speed(self):
        """
        @return : (speed in, speed out)
        @rtype  : tuple
        """

        return self.__swap.poll()


    # The following functions will be overriden in a subclass (Generic, ...).
    def net_devices(self):
        return []


    def cpu_model(self):
        return ""


    def cpu_speed(self):
        return 0.0


    def cpu_cache(self):
        return 0


    def cpu_bogomips(self):
        return 0.0

