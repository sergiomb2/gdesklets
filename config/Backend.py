#
# Python's shelve module comes broken on more and more systems, so we have to
# use our own backend. This makes it all more portable also.
#


_MAGIC = "GDESKLETS"


class _Backend(dict):

    def __init__(self, filename, load = True):

        self.__dbfile = filename

        dict.__init__(self)

        if (load):
            try:
                self.__load()
            except:
                pass


    def __load(self):

        import cPickle
        data = open(self.__dbfile, "r").read()[len(_MAGIC):]
        self.clear()
        self.update(cPickle.loads(data))


    def __save(self):

        import cPickle
        data = cPickle.dumps(self.copy())
        fd = open(self.__dbfile, "w")
        fd.write(_MAGIC)
        fd.write(data)
        fd.close()


    def sync(self):

        self.__save()


    def set_file(self, path):

        self.__dbfile = path
        
        
#
# Factory function for the backend.
#
def Backend(filename, *args):

    try:
        header = open(filename).read(len(_MAGIC))
    except:
        header = _MAGIC
        
    if (header == _MAGIC):
        backend = _Backend(filename)
    else:
        # migrate legacy stuff to new format (hello seb128!)
        import shelve
        legacy = shelve.open(filename, flag = "c", writeback = False)
        backend = _Backend(filename, load = False)
        backend.update(legacy)

    return backend
