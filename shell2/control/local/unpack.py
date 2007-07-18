import os
import commands
import tempfile
import dircache
import shutil


def unpack(package, to, validate_against_name = None):
    ''' Unpack the "package" and move all directories inside to the directory "to".
        First creates a temporary directory, unpacks everything there
        and then moves the files to the "to" dir '''
    
    print "unpack called with", package, "->", to
    file = os.path.abspath(package)
    dir = tempfile.mkdtemp()
    try:
        os.mkdir(to)
    except OSError:
        pass
        #print "unpack.py: could not display dir (already exists?)"
    
    print "unpack.py: created temp dir ", dir
    
    # determine archive type
    head = open(file, "r").read(3)
    if (head.startswith("BZh")):
        cmd = "cd \"%s\" && tar -xjf \"%s\"" % (dir, file)
    elif (head.startswith("\x1f\x8b")):
        cmd = "cd \"%s\" && tar -xzf \"%s\"" % (dir, file)
    else:
        raise IOError("unpack.py: file %s is of unknown type." % (file) )

    fail, out = commands.getstatusoutput(cmd)
    if (fail): raise IOError(out)
    
    # dir(s) inside the package are now in the temp dir "dir"
    dirs = __find_dirs_under(dir)
    
    # we can only handle one dir inside the parent. If there were many we would need
    # to have Widget.local_path as an array and it would complicate things 
    if len(dirs) > 1:
        raise "unpack.py: Multiple directories under desklet package %s (unpacked to %s). Aborting. " % (package, dir)
    
    d = dirs[0]
    
    abs_from_path = os.path.join(dir, d)
    abs_to_path = os.path.join(to, d)
        
    if validate_against_name is not None:
        if d != validate_against_name:
            print "unpack.py: package dir %s does not equal to name %s. Renaming.." % (d, validate_against_name)
            abs_to_path = os.path.join(to, validate_against_name)
    try: 
        shutil.move(abs_from_path, abs_to_path)
        print "unpack.py: moved %s to %s" % (abs_from_path, abs_to_path)
    except OSError:
        # this probably means that the target dir exists 
        # (a desklet with the same name has been installed)
        print "unpack.py: the directory %s already exists" % (abs_to_path)
    
    return abs_to_path # return the final destination so that the widget may update local_path
    


def __find_dirs_under(path):
    dirs = []
    for dir in dircache.listdir(path):
        if os.path.isdir(os.path.join(path, dir)): dirs.append(dir)
    
    print dirs
    return dirs
        
        
    
def find_displays(self):

    def f(file): return (os.path.splitext(file)[1] == ".display")
    values = self.__find(self.__dir, f)
    return [os.path.dirname(p) for p in values]



def find_controls(self):

    def f(file): return (file == "controls")
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

