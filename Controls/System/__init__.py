from libdesklets.controls import Control, FakeSelf
from libdesklets import system

from ISystem import ISystem


class System(Control, ISystem):

    def __init__(self):

        Control.__init__(self)

        self.__allfs = False
        self.__dev   = ""
        self.__mdir  = ""
        self.__pid   = 0
        self.__which = 0



    def __get_allfs(self):

        return self.__allfs

    def __set_allfs(self, bval):

        self.__allfs = bval
        self._update("allfs")



    def __get_mdir(self):

        return self.__mdir

    def __set_mdir(self, val):

        self.__mdir = val
        self._update("mountdir")



    def __get_dev(self):

        return self.__dev

    def __set_dev(self, val):

        self.__dev = val
        self._update("device")



    def __get_pid(self):

        return self.__pid

    def __set_pid(self, val):

        self.__pid = val
        self._update("pid")


    def __get_which(self):

        return self.__which

    def __set_which(self, val):

        self.__which = val
        self._update("which")


    def __get_fsusage(self):

        return system.fsusage(self.__mdir)

    def __get_net_load(self):

        return system.net_load(self.__dev)

    def __get_net_speed(self):

        return system.net_speed(self.__dev)

    def __get_net_state(self):

        return system.net_state(self.__dev)

    def __get_ppp(self):

        return system.ppp(self.__dev)

    def __get_proc_args(self):

        return system.proc_args(self.__pid)

    def __get_proc_kernel(self):

        return system.proc_kernel(self.__pid)

    def __get_proc_list(self):

        return system.proc_list(self.__which, self.__pid)

    def __get_proc_map(self):

        return system.proc_map(self.__pid)

    def __get_proc_mem(self):

        return system.proc_mem(self.__pid)

    def __get_proc_segment(self):

        return system.proc_segment(self.__pid)

    def __get_proc_signal(self):

        return system.proc_signal(self.__pid)

    def __get_proc_state(self):

        return system.proc_state(self.__pid)

    def __get_proc_time(self):

        return system.proc_time(self.__pid)

    def __get_proc_uid(self):

        return system.proc_uid(self.__pid)



    allfs            = property(__get_allfs, __set_allfs,
                                doc = "Getter/Setter for boolean allfs")
    iface            = property(__get_dev, __set_dev,
                                doc = "Getter/Setter for network interface")
    mountdir         = property(__get_mdir, __set_mdir,
                                doc = "Getter/Setter for mountdir")
    pid              = property(__get_pid, __set_pid,
                                doc = "Getter/Setter for pid")
    which            = property(__get_which, __set_which,
                                doc = "Getter/Setter for which")

    cpu              = property(FakeSelf(system.cpu), doc = "General CPU info")
    cpu_bogomips     = property(FakeSelf(system.cpu_bogomips),
                                         doc = "CPU bogomips")
    cpu_cache        = property(FakeSelf(system.cpu_cache),
                                doc = "CPU 2nd level cache")
    cpu_clock        = property(FakeSelf(system.cpu_speed), doc = "CPU clock")
    cpu_load         = property(FakeSelf(system.cpu_load), doc = "CPU load")
    cpu_model        = property(FakeSelf(system.cpu_model), doc =  "CPU model")

    fsusage          = property(__get_fsusage,
                                doc = "Information of given mounted filesystem")
    hostname         = property(FakeSelf(system.hostname),
                                doc = "The machine's hostname")
    kernel_version   = property(FakeSelf(system.kernel_version),
                                doc = "Kernel version")
    loadavg          = property(FakeSelf(system.loadavg),
                                doc = "Average load info")
    memory           = property(FakeSelf(system.mem), doc = "Memory information")
    mountlist        = property(FakeSelf(system.mountlist),
                                doc = "(All) mountpoints")
    net_devices       = property(FakeSelf(system.netlist),
                                doc = "Available network devs")
    net_load         = property(__get_net_load, doc = "Netload of given device")
    net_speed        = property(__get_net_speed,
                                doc = "Incoming / Outgoing traffic speed of "
                                      "given device")
    net_state        = property(__get_net_state, doc = "Device up or down")

    operating_system = property(FakeSelf(system.operating_system),
                                doc = "Type of operating system")
    ppp              = property(__get_ppp, doc = "Point-to-Point information")
    proc_args        = property(__get_proc_args,
                                doc = "Command line args of process ID")
    proc_kernel      = property(__get_proc_kernel, doc = "")
    proc_list        = property(__get_proc_list, doc = "")
    proc_map         = property(__get_proc_map, doc = "")
    proc_mem         = property(__get_proc_mem, doc = "")
    proc_segment     = property(__get_proc_segment, doc = "")
    proc_signal      = property(__get_proc_signal, doc = "")
    proc_state       = property(__get_proc_state, doc = "")
    proc_time        = property(__get_proc_time, doc = "")
    proc_uid         = property(__get_proc_uid, doc = "")
    swap             = property(FakeSelf(system.swap),
                                doc = "Swap space information")
    uptime           = property(FakeSelf(system.uptime),
                                doc = "Uptime information")
    users            = property(FakeSelf(system.users), doc ="Number of users")



def get_class(): return System
