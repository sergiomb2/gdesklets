from libdesklets.system.Arch import Arch

import re
import struct


class Generic(Arch):

    def __init__(self):

        Arch.__init__(self)

        self.__net_devices = re.compile('^\s*(\w+):.*mtu', re.M
                                        ).findall( os.popen('/sbin/ifconfig -a').read() )

        # just get the first cpu0 line

        # cpu0: Intel Celeron (Mendocino) ("GenuineIntel" 686-class, 128KB L2 cache) 468 MHz
        # cpu0: FPU,V86,DE,PSE,TSC,MSR,PAE,MCE,CX8,SEP,MTRR,PGE,MCA,CMOV,PAT,PSE36,MMX,FXSR

        m = re.search('^cpu0: (.*?) \(.*?\)* (\d+) MHz$',
                      open("/var/run/dmesg.boot").read(),
                      re.MULTILINE)

        self.__model = m.group(1)
        self.__speed = m.group(2)



    def net_devices(self):
        """
        @return : all available network devices
        @rtype  : list
        """

        return (self.__net_devices)



    def cpu_model(self):
        """
        @return : model/type of installed processor
        @rtype  : str
        """

        return (self.__model)



    def cpu_speed(self):
        """
        @return : current clock of installed processor
        @rtype  : float
        """

        return float(self.__speed)



    def users(self):
        """
        @return : number of connected users
        @rtype  : int
        """

        # man utmp
        # don't know if
        # sizeof(struct utmp) == 300
        # offsetof(struct utmp, ut_name) == 8
        # on every OpenBSD arch
        # sparc64 : ok

        count = 0
        data = open('/var/run/utmp', 'rb').read()

        for i in range(8, len(data), 300):

            ut_name = struct.unpack('c', data[i:i+1])[0]

            if (ut_name != '\0'):
                count += 1

        return count
