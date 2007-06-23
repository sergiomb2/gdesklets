import threading


def locked(f, lock):

    def helper(*args, **kw):

        lock.acquire()

        try:
            return f(*args, **kw)
        finally:
            lock.release()

    return helper


class SyncWriter(object):

    __slots__ = ('__stream', 'write', 'writelines', 'flush')

    def __init__(self, stream):

        self.__stream = stream

        lock = threading.RLock()

        self.write      = locked(stream.write,      lock)
        self.writelines = locked(stream.writelines, lock)
        self.flush      = locked(stream.flush,      lock)


    def __getattr__(self, name):

        return getattr(self.__stream, name)

