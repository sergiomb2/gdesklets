from main import _

import struct
import socket

_TERA = 2**40
_GIGA = 2**30
_MEGA = 2**20
_KILO = 2**10


def human_readable_bytes(bytes):

    try:
         import gnomevfs
         return gnomevfs.format_file_size_for_display(bytes)
    except ImportError:

        global _TERA, _GIGA, _MEGA, _KILO

        if bytes >= _TERA:
            return _("%.2f TB") % (float(bytes) / _TERA)
        elif bytes >= _GIGA:
            return _("%.2f GB") % (float(bytes) / _GIGA)
        elif bytes >= _MEGA:
            return _("%.2f MB") % (float(bytes) / _MEGA)
        elif bytes >= _KILO:
            return _("%.2f kB") % (float(bytes) / _KILO)
        else:
            return _("%d B") % bytes



def bytes_to_gmkb(bytes):
    global _TERA, _GIGA, _MEGA, _KILO

    gigs, bytes = divmod(bytes, _GIGA)
    megs, bytes = divmod(bytes, _MEGA)
    ks  , bytes = divmod(bytes, _KILO)

    return (gigs, megs, ks, bytes)



def gmkb_to_bytes(gigs, megs, ks, bytes):
    global _TERA, _GIGA, _MEGA, _KILO

    b  = gigs * _GIGA
    b += megs * _MEGA
    b += ks   * _KILO
    b += bytes

    return b


def secs_to_dhms(secs):

    day,  secs = divmod(secs, 86400)
    hou,  secs = divmod(secs, 3600)
    mint, secs = divmod(secs, 60)

    return (day, hou, mint, secs)



def dhms_to_secs(d, h, m, s):

    secs  = 86400 * d
    secs += 3600 * h
    secs += 60 * m
    secs += s

    return secs



def centigrade_to_fahrenheit(c):

    return (c * 1.8) + 32.0



def fahrenheit_to_centigrade(f):

    return (f - 32.0) / 1.8



def centigrade_to_kelvin(c):

    return c + 273.16



def kelvin_to_centigrade(k):

    return k - 273.16



def ipv4_to_dotted_quad(ip):

    """Converts ipv4 (32bits unsigned integer) to
    dotted-quad decimal representation

    e.g:
      ipv4_to_dotted_quad(1291888832)
        -> '192.168.0.77'
    """
    return socket.inet_ntoa(struct.pack('=L', ip))



def dotted_quad_to_ipv4(ip):

    """Converts dotted-quad decimal to
     ipv4 (32bits unsigned integer) representation

    e.g:
      dotted_quad_to_ipv4('192.168.0.77')
        -> 1291888832
    """
    return struct.unpack('=L', socket.inet_aton(ip))[0]



if __name__ == "__main__":
    print human_readable_bytes(100000000)
    print human_readable_bytes(1232348749)

