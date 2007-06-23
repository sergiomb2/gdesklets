from Generic import Generic

import re


class PPC(Generic):

    def __init__(self):

        Generic.__init__(self)

        def _get_model():
            r = re.compile('^cpu\s+:\s+(.+)$', re.M)
            m = r.search( self._read_cpuinfo() )
            return m.group(1)

        def _get_cache():
            r = re.compile('^L2 cache\s+:\s+(\d+)', re.M)
            m = r.search( self._read_cpuinfo() )
            return int(m.group(1))

        # CPU model and cache size never changes
        self.__model_name = _get_model()
        self.__cache_size = _get_cache()

        # the cpu speed might change (laptops have mobile CPUs)
        self.__speed      = re.compile('^clock\s+:\s+(\d+)', re.M)



    def cpu_speed(self):
        """
        @return : current clock of installed processor
        @rtype  : float
        """

        m = self.__speed.search( self._read_cpuinfo() )
        return float(m.group(1))



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
