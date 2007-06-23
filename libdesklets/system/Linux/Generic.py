from libdesklets.system.Arch import Arch

import re
import struct


class Generic(Arch):

    def __init__(self):

        Arch.__init__(self)

        self.__bogomips    = re.compile('^bogomips\s+:\s+(\d+\.\d+)$', re.M)
        self.__net_devices = re.compile('^\s*(\w+):', re.M)


    def _read_cpuinfo(self):
        """
        @return : content of the pseudo file /proc/cpuinfo
        @rtype  : str
        """

        return open('/proc/cpuinfo').read()



    def net_devices(self):
        """
        @return : all available network devices
        @rtype  : list
        """

        data = open('/proc/net/dev').read()
        return self.__net_devices.findall(data)



    def cpu_bogomips(self):
        """
        @return : bogomips of installed processor
        @rtype  : float
        """

        m = self.__bogomips.search( self._read_cpuinfo() )
        return float(m.group(1))



    def users(self):
        """
        @return : number of connected users
        @rtype  : int
        """

        # man utmp
        # don't know if
        # sizeof(struct utmp) == 384
        # sizeof(short) == 2
        # on every Linux arch
        # http://gnomesupport.org/forums/viewtopic.php?p=33686
        # X86, X86_64 : ok

        count = 0
        data = open('/var/run/utmp', 'rb').read()

        for i in range(0, len(data), 384):

            ut_type = struct.unpack('h', data[i:i+2])[0]

            if (ut_type == 7):
                count += 1

        return count
