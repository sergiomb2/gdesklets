from plugin.ControlRegistry import ControlRegistry
from plugin.Interface import Interface
from main import CONTROLPATHS, HOME

import os
import sys


if os.curdir not in sys.path: sys.path.append(os.curdir)
if HOME not in sys.path: sys.path.append(HOME)


#
# Factory for plugins. We don't look up plugins by their implementation but
# by their interface. Several plugins providing the same interface may
# co-exist.
#
class _ControlFactory:

    def __init__(self):

        self.__after_rebuilding = False

        self.__registry = ControlRegistry(CONTROLPATHS)
        


    #
    # Returns a control providing the given interface.
    #
    def get_control(self, iface):

        ctrl = self.__registry.get_control(iface)
        if (ctrl and os.path.isdir(ctrl)):
            cwd = os.getcwd()
            os.chdir(os.path.dirname(ctrl))
            m = __import__(os.path.basename(ctrl))
            obj = m.get_class()()
            os.chdir(cwd)
            return obj
        else:
            return None



_singleton = _ControlFactory()
def ControlFactory(): return _singleton
