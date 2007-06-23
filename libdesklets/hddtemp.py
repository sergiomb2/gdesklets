import socket
import re
import sys

from utils.Struct import Struct
from libdesklets import convert


__HOST = 'localhost'
__PORT = 7634
# __SEPARATOR = '|'
__REGEX = re.compile('\|(?P<device>.+?)\|(?P<name>.+?)\|(?P<value>\d+)\|(?P<unit>[CF])\|')


def __split(data):
    
    # |/dev/hda|TOSHIBA MK6025GAS|50|C|
    # |/dev/hda|MAXTOR 6L040J2|41|C||/dev/hdh|IC35L040AVVN07-0|39|C|
    
    def match_to_struct(m):

        value = float(m['value'])
        unit  = m['unit']
        
        assert unit in ('C', 'F')

        if   unit == 'C':
            C = value
        elif unit == 'F':
            C = convert.fahrenheit_to_centigrade(value)
        
        F = convert.centigrade_to_fahrenheit(C)
        K = convert.centigrade_to_kelvin(C)

        return Struct(device = m['device'],
                      name   = m['name'],
                      temp   = Struct(centigrade = C,
                                      fahrenheit = F,
                                      kelvin     = K
                                      )
                      )

    return [ match_to_struct(m.groupdict()) for m in __REGEX.finditer(data) ]



def __socket_read():    

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((__HOST, __PORT))
    return s.makefile().read()




def poll_all():
    
    try:
        return __split( __socket_read() )
    except Exception, exc:
        log("Cannot retrieve HDD temperature. Error was %s" % (exc,))
        return []



def available_devices():
    
    return [ s.device for s in poll_all() ]



def poll(device):

    for s in poll_all():

        if s.device == device:
            return s

    else:
        log("Cannot retrieve HDD temperature for device %s." % (device,))
        return None




if __name__ == '__main__':

    print available_devices()
    print poll('/dev/hda')
    print poll_all()
    print poll('/dev/uba')

