from Generic import Generic

import re
import struct

# Also works for x86_64
# it seems that there's no difference

class X86(Generic):

    def __init__(self):

        Generic.__init__(self)

        def _get_model():
            r = re.compile('^model name\s+:\s+(.+)$', re.M)
            m = r.search( self._read_cpuinfo() )
            return m.group(1)

        def _get_cache():
            r = re.compile('^cache size\s+:\s+(\d+)\sKB$', re.M)
            m = r.search( self._read_cpuinfo() )
            return int(m.group(1))

        # CPU model and cache size never changes
        self.__model_name = _get_model()
        self.__cache_size = _get_cache()

        # the cpu speed might change (laptops have mobile CPUs)
        self.__speed      = re.compile('^cpu MHz\s+:\s+(\d+\.\d+)$', re.M)



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

        m = self.__speed.search( self._read_cpuinfo() )
        return float(m.group(1))



    def users(self):

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
            if (ut_type == 7): count += 1

        return count

