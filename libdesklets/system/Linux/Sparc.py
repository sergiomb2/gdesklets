from Generic import Generic

import re


class Sparc(Generic):

    def __init__(self):

        Generic.__init__(self)

        def _get_model():
            r = re.compile('^cpu\s+:\s+(\w+)$', re.M)
            m = r.search( self._read_cpuinfo() )
            return m.group(1)

        # CPU model and cache size never changes
        self.__model_name = _get_model()
        self.__cache_size = _get_cache()

        # the cpu speed might change (laptops have mobile CPUs)
        self.__speed = re.compile('^Cpu0ClkTck\s+:\s+(\w+)$', re.M)
        self.__bogo  = re.compile('^Cpu0Bogo\s+:\s+(\d+\.\d+)$', re.M)



    def cpu_speed(self):
        """
        @return : current clock of installed processor
        @rtype  : float
        """

        m = self.__speed.search( self._read_cpuinfo() )
        return float(int(m.group(1), 0x10))



    def cpu_bogomips(self):
        """
        @return : bogomips of installed processor
        @rtype  : float
        """

        m = self.__bogo.search( self._read_cpuinfo() )
        return float(m.group(1))



    def cpu_model(self):
        """
        @return : model/type of installed processor
        @rtype  : str
        """

        return self.__model_name
