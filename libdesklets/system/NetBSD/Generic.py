from libdesklets.system.Arch import Arch

import re
import struct


class Generic(Arch):

    def __init__(self):

        Arch.__init__(self)

        self.__net_devices = re.compile('^\s*(\w+):.*mtu', re.M
                                        ).findall( os.popen('/sbin/ifconfig -a').read() )

        # cpu0 at mainbus0: MIPS R3000A CPU (0x230) Rev. 3.0 with MIPS R3010 FPC Rev. 3.0
        # cpu0: 64KB/4B direct-mapped Instruction cache, 64 TLB entries
        # cpu0: 64KB/4B direct-mapped write-through Data cache

        m = re.compile('^cpu0 at mainbus0: (.*?) CPU', re.M
                       ).search(open("/var/run/dmesg.log").read() )

        self.__model = m.group(1)



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



    def users(self):
        """
        @return : number of connected users
        @rtype  : int
        """

        # man utmp
        # don't know if
        # sizeof(struct utmp) == 36
        # offsetof(struct utmp, ut_name) == 8
        # on every NetBSD arch
        # mips3000 : ok

        count = 0
        data = open('/var/run/utmp', 'rb').read()

        for i in range(8, len(data), 36):

            ut_name = struct.unpack('c', data[i:i+1])[0]

            if (ut_name != '\0'):
                count += 1

        return count
