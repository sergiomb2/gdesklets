from libdesklets.system.Arch import Arch

import re
import struct
import os

class Generic(Arch):

    def __init__(self):

        Arch.__init__(self)

        self.__net_devices = re.compile('^\s*(\w+):.*mtu', re.M
                                        ).findall( os.popen('/sbin/ifconfig -a').read() )



    def net_devices(self):
        """
        @return : all available network devices
        @rtype  : list
        """

        return (self.__net_devices)



    def users(self):
        """
        @return : number of connected users
        @rtype  : int
        """

        # man utmp
        # don't know if
        # sizeof(struct utmp) == 44
        # offsetof(struct utmp, ut_name) == 8
        # on every FreeBSD arch

        count = 0
        data = open('/var/run/utmp', 'rb').read()

        for i in range(8, len(data), 44):

            ut_name = struct.unpack('c', data[i:i+1])[0]

            if (ut_name != '\0'):
                count += 1

        return count
