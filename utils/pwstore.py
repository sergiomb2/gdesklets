#
# Module for storing confidential data like passwords.
#
# This was modeled after the mozilla password storage system with some security
# improvements; in fact it looks totally different.
#
# This one uses a prefix where to store the key file. Don't ever let somebody
# read your key file!
# The keys are worthless without the key file and vice versa.
#

import utils


import random
import os
import base64



def _init_store(prefix):

    l = os.listdir(prefix)
    l.sort()
    if (not (l and l[0].startswith(".!pwstore"))):
        _create_store(prefix)



def _create_store(prefix):

    r1 = random.randrange(0xffffffL, 0x7fffffffL)
    r2 = random.randrange(0xffffffL, 0x7fffffffL)
    fname1 = ".!pwstore" + str(r1)
    fname2 = ".!" + str(r2)
    utils.makedirs(os.path.join(prefix, fname1))
    path = os.path.join(prefix, fname1, fname2)

    # is this equivalent to the commented code below? i think so
    # chars = [chr(a) for a in range(256)*16 if a!=26]
    # better :D
    chars = [chr(a) for a in range(256) if a!=26] * 16
    #chars = []
    #for i in xrange(4096):
    #    a = i % 256
    #    if (a == 26): continue
    #    chars.append(chr(a))
    #end for

    data = ""
    while chars:
        index = random.randrange(len(chars))
        c = chars.pop(index)
        data += c
    #end while

    fd = open(path, "w")
    fd.write(data)
    fd.close()
    os.chmod(path, 0400)



def _open_store(prefix):

    try:
        l = os.listdir(prefix)
        l.sort()
        fname1 = l[0]
        l = os.listdir(os.path.join(prefix, fname1))
        fname2 = l[0]

        path = os.path.join(prefix, fname1, fname2)
        data = open(path).read()

        return data

    except OSError:
        return



#
# Stores the given value and returns a key for retrieval.
#
def store(prefix, value):

    _init_store(prefix)
    data = _open_store(prefix)

    v64 = base64.encodestring(repr(value))
    key = u""
    for c in v64:
        index = data.index(c)
        key += unichr(index)
    #end for

    return repr(key)



#
# Returns the value for the given key.
#
def retrieve(prefix, key):

    if (not key): return ""

    _init_store(prefix)
    data = _open_store(prefix)

    try:
        v64 = ""
        for c in eval(key):
            v64 += data[ord(c)]
	#end for

	value = eval(base64.decodestring(v64))
	return value

    except base64.binascii.Error:
        return ""
