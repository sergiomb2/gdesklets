''' Functions that activate, deactivate and fetch the open displays.

    This interface works with the 0.35.x versions of gdesklets. '''

import os
import urllib

_DISPLAYLIST = None

def initialize(home_dir):
    global _DISPLAYLIST, _DSPLIST
    _DISPLAYLIST = os.path.join(home_dir, "displays")
    


def get_active_desklets():
    ''' Gets all the active displays as paths and returns results '''
    global _DISPLAYLIST
    
    profiles = {}
    path_table = {}
    profiles_table = {}
    
    print "opening", _DISPLAYLIST
    try:
        data = open(_DISPLAYLIST, "r").readlines()
    except IOError, exc:
        return

    try:
        current_profile = data.pop(0).strip()
    except IndexError, exc:
        log("The displaylist file has wrong format, ignoring it.")
        return

    profiles[current_profile] = []
    displays = []
    
    for line in data:
        if (not line): continue

        try:
            ident, path, profile = line.split()
        except ValueError, exc:
            print "The displaylist file has wrong format, ignoring it."
            return

        path = unescape_path(path)
        profile = unescape_path(profile)
        if (not profile in profiles):
            profiles[profile] = []
        profiles[profile].append(ident)
        
        displays.append(path)
        path_table[ident] = path
        profiles_table[ident] = profile
        
    return displays



def activate(path):
    ''' Activates the given display '''
    os.system("gdesklets open \"%s\"" % (path))
        


def deactivate(path):
    ''' Shuts down the given display '''
    pass
    
    

def unescape_path(uri):
    return urllib.unquote(uri)



def escape_path(uri):
    return urllib.quote(uri)
    
        