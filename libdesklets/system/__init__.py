import ArchFactory
from gtop import *

# deprecated
proc_list = proclist
net_load = netload

_arch = ArchFactory.create_arch()

net_devices  = _arch.net_devices
net_speed    = _arch.net_speed
net_state    = _arch.net_state

cpu_bogomips = _arch.cpu_bogomips
cpu_cache    = _arch.cpu_cache
cpu_load     = _arch.cpu_load
cpu_model    = _arch.cpu_model
cpu_speed    = _arch.cpu_speed

kernel_version    = _arch.kernel_version
hostname          = _arch.hostname
operating_system  = _arch.operating_system
users             = _arch.users

