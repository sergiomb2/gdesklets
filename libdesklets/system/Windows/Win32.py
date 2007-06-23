from libdesklets.system.Arch import Arch

import os
import sys


class Win32(object):

    def __init__(Arch):

        Arch.__init__(self)


    def kernel_version(self):

        return ""


    def hostname(self):

        return ""


    def operating_system(self):

        return ""


    def net_speed(self):

        return (0, 0)


    def net_state(self, dev):

        return 0


    def cpu_load(self):

        return 0.0


    def cpu_count(self):

        return 0


    def all_cpu_load(self):

        return []


    def swap_speed(self):

        return (0, 0)


    def net_devices(self):

        return []


    def cpu_model(self):

        return ""


    def cpu_speed(self):

        return 0.0


    def cpu_cache(self):

        return 0


    def cpu_bogomips(self):

        return 0.0


    def users(self):

        return 0
