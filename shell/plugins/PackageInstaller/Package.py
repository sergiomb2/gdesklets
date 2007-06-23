import os
import commands
import tempfile


_BZIP2 = 0
_GZIP = 1


#
# Class for accessing desklet packages.
#
class Package:

    def __init__(self, file):

        file = os.path.abspath(file)
        self.__dir = tempfile.mktemp()
        os.mkdir(self.__dir)

        # determine archive type
        head = open(file, "r").read(3)
        if (head.startswith("BZh")):
            cmd = "cd \"%s\" && bzip2 -dc \"%s\" | tar -xf -" % (self.__dir, file)
        elif (head.startswith("\x1f\x8b")):
            cmd = "cd \"%s\" && gzip -dc \"%s\" | tar -xf -" % (self.__dir, file)
        else:
            raise IOError("Unknown file type.")

        fail, out = commands.getstatusoutput(cmd)
        if (fail): raise IOError(out)



    def close(self):

        os.system("rm -rf \"%s\"" % (self.__dir))


    def find_displays(self):

        def f(file): return (os.path.splitext(file)[1] == ".display")
        values = self.__find(self.__dir, f)
        return [os.path.dirname(p) for p in values]



    def find_controls(self):

        def f(file): return (file == "controls")
        return self.__find(self.__dir, f)


    def find_sensors(self):

        def f(file): return (file[:7] == "Install" and
                             os.path.splitext(file)[1] == ".bin")
        return self.__find(self.__dir, f)



    def __find(self, path, predicate):

        if (not path): path = self.__dir
        values = []
        files = os.listdir(path)
        for f in files:
            if (predicate(f)):
                values.append(os.path.join(path, f))
            elif (os.path.isdir(os.path.join(path, f))):
                values += self.__find(os.path.join(path, f), predicate)
        #end for

        return values


    def install_displays(self, dest):

        pass



    def install_controls(self, dest):

        pass


    def install_sensors(self, dest):

        pass
