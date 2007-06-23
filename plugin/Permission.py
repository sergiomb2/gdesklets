__all__ = ('READWRITE', 'READ', 'WRITE', 'DENY', 'Permission')


class _Permission(object):

    READ  = 0x4
    WRITE = 0x2

    __slots__ = ('__mode',)


    def __init__(self, prop):

        self.__mode = 0x0

        if prop.fget:
            self.__mode |= _Permission.READ

        if prop.fset:
            self.__mode |= _Permission.WRITE



    def __get_readable(self):
        return self.__mode & _Permission.READ

    def __get_writable(self):
        return self.__mode & _Permission.WRITE

    Readable = property(__get_readable)
    Writable = property(__get_writable)



    def __str__(self):

        s = ''

        if self.Readable:
            s += 'r'
        if self.Writable:
            s += 'w'

        return s



    def __int__(self):

        return self.__mode




class __Foo(object):

    read  = property(fget=int)
    write = property(fset=int)
    rw    = property(fget=int, fset=int)
    deny  = property(fget=None, fset=None)




READ      = _Permission(__Foo.read)
WRITE     = _Permission(__Foo.write)
READWRITE = _Permission(__Foo.rw)
DENY      = _Permission(__Foo.deny)




def Permission(prop = None):

    if not prop:
        return DENY

    if prop.fget and prop.fset:
        return READWRITE

    elif prop.fget:
        return READ

    elif prop.fset:
        return WRITE
