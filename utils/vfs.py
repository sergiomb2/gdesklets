#
# Abstraction layer for VFS operations to move gnomevfs dependency out of the
# core.
#

USE_GNOMEVFS = True

import urllib

try:
    import gnomevfs

    OPEN_READ = gnomevfs.OPEN_READ
    OPEN_WRITE = gnomevfs.OPEN_WRITE

except ImportError:
    try:
        import gnome.vfs as gnomevfs

        OPEN_READ = gnomevfs.OPEN_READ
        OPEN_WRITE = gnomevfs.OPEN_WRITE

    except ImportError:
        log("Using urllib, because gnomevfs isn't available")
        OPEN_READ = "r"
        OPEN_WRITE = "w"

        USE_GNOMEVFS = False



def escape_path(uri):

    try:
        return gnomevfs.escape_string(uri)
    except:
        return escape_path_urllib(uri)

def escape_path_urllib(uri):

    return urllib.quote(uri)



def unescape_path(uri):

    return urllib.unquote(uri)



#
# Reads the entire file and returns its contents.
#
def read_entire_file(uri):

    try:
        uri = gnomevfs.read_entire_file(uri)
    except:
        log("Warning: Couldn't read file \"%s\"." % (uri,))
        raise

    return uri

def read_entire_file_urllib(uri):

    if (not "://" in uri): uri = "file://" + uri

    try:
        uri = urllib.urlopen(uri).read()
    except:
        log("Warning: Couldn't read file \"%s\"." % (uri,))
        raise

    return uri



#
# Opens the given URI and returns a file descriptor.
#
def open(uri, mode = OPEN_READ):

    try:
        fd = gnomevfs.open(uri, mode)
    except:
        log("Warning: Couldn't open file \"%s\"." % (uri,))
        return

    return fd

def open_urllib(uri, mode = OPEN_READ):

    if (not "://" in uri): uri = "file://" + uri

    try:
        fd = urllib.urlopen(uri)
    except:
        log("Warning: Couldn't open file \"%s\"." % (uri,))
        return

    return fd



#
# Returns whether the given URI exists.
#
def exists(uri):

    return gnomevfs.exists(gnomevfs.URI(uri))

def exists_urllib(uri):

    if (not "://" in uri): uri = "file://" + uri

    try:
        urllib.urlopen(uri)
    except:
        return False
    else:
        return True



if (not USE_GNOMEVFS):
    read_entire_file = read_entire_file_urllib
    open = open_urllib
    exists = exists_urllib
    escape_path = escape_path_urllib
