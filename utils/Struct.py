# from libdesklets.system.gtop import _Struct as Struct

class Struct(dict):

    """
    Class for smart handling a bunch of data.

    The following is a example
      >>> s = Struct(spam=42, egg=range(3))
      >>> print s, s.spam, s.egg
      {'egg': [0, 1, 2], 'spam': 42} 42 [0, 1, 2]

      >>> stat = get_system_information()
      >>> display(stat.info1)

    """

    __slots__ = ()

    def __getattr__(self, name):

        return self[name]



    def __repr__(self):

        s = 'Struct {'

        items = self.items()
        items.sort()

        for k, v in items:

            s += ' .%s = %s,' % (k, v)

        if s[-1] == ',':
            s = s[:-1]

        s += ' }'

        return s


    def __hash__(self):

        return hash(repr(self))

