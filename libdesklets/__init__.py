#
# Library for common functionality.
#

# convert
#   human_readable_bytes(bytes:int): (int)
#   bytes_to_gmkb(bytes:int): (int, int, int, int)
#   gmkb_to_bytes(GB:int, MB:int, kB:int, Bytes:int): (bytes:int)
#   secs_to_dhms(secs:int): (days:int, hrs:int, mins:int, secs:int)
#   dmhs_to_secs(days:int, hrs:int, mins:int, secs:int)
#   centigrade_to_fahrenheit(centigrade:int): (fahrenheit:int)
#   fahrenheit_to_centigrade(fahrenheit:int): (centigrade:int)
#   centigrade_to_kelvin(centigrade:int): (kelvin:int)
#   kelvin_to_centigrade(kelvin:int): (centigrade:int)

from convert import *

from utils.Struct import Struct
