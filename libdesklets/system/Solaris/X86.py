from Generic import Generic

import re
import struct
import os

# Also works for x86_64
# it seems that there's no difference

class X86(Generic):

    def __init__(self):

        Generic.__init__(self)

        def _get_model():
            r = re.compile('^.*brand-string.*\n\s+value=(.+)$', re.M)
            m = r.findall( self._read_cpuinfo() )
            return m[0]

        def _get_cache():
            r = re.compile('^.*l2-cache-size.*\n\s+value=(.+)$', re.M)
            m = r.findall( self._read_cpuinfo())
            m_int = int(m[0],16)
            return int(round(m_int/1000))

        def _read_cpu_speed():
            r = re.compile('^.*cpu-mhz.*\n\s+value=(.+)$', re.M)
            m = r.findall(self._read_cpuinfo())
            return float(int(m[0],16))

        # CPU model and cache size never changes
        self.__model_name = _get_model()
        self.__cache_size = _get_cache()

        # the cpu speed might change (laptops have mobile CPUs)
        self.__speed = _read_cpu_speed()


    def _read_cpuinfo(self):
            """
            @return : content of cpu_info
            @rtype  : str
            """
            return os.popen('/usr/sbin/prtconf -v').read()


    def cpu_cache(self):
        """
        @return : 2nd level cache of installed processor
        @rtype  : int
        """

        return self.__cache_size


    def cpu_model(self):
        """
        @return : model/type of installed processor
        @rtype  : str
        """

        return self.__model_name


    def cpu_speed(self):
        """
        @return : current clock of installed processor
        @rtype  : float
        """
        return self.__speed


    def users(self):

        count = 0
        data = open('/var/adm/utmpx', 'rb').read()

        for i in range(0, len(data), 384):
            ut_type = struct.unpack('h', data[i:i+2])[0]

            if (ut_type == 7):
                count += 1

        return count

