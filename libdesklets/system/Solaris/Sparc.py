from Generic import Generic

import os
import re


class Sparc(Generic):

    def __init__(self):

        Generic.__init__(self)

        def _get_model():
            r = re.compile('brand\s+(.+)$', re.M)
            m = r.findall( self._read_cpuinfo() )
            return m[0]

        def _get_cache():
            r = re.compile('^\s+ecache-size:+\s+(.+)$',re.M)
            m = r.findall(os.popen('/usr/sbin/prtconf -vp').read())
            m_int = int(m[0],16)
            return int(round(m_int/1000))

        def _read_cpu_speed():
            r = re.compile('clock_MHz\s+(\d+)$', re.M)
            m = r.findall(self._read_cpuinfo())
            return float(int(m[0]))

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
            return os.popen('/usr/bin/kstat cpu_info').read()

    def cpu_speed(self):
        """
        @return : current clock of installed processor
        @rtype  : float
        """

        return self.__speed


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
