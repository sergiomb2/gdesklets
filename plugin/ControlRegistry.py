from main import HOME, REGISTRY_PATH
from plugin.Interface import Interface
from utils.MetaDataRegistry import MetaDataRegistry
from utils import vfs

import commands
import os

_REGFILE = os.path.join(REGISTRY_PATH, "controls.reg")


class ControlRegistry:
    """
    Class for holding a registry of controls. The registry is saved to a
    'controls.reg' file in order to speed up the startup process, since cached
    information can be used.
    """


    def __init__(self, repos):

        self.__registry = {}

        self.__mdreg = MetaDataRegistry(_REGFILE, repos,
                                        self.__find_controls,
                                        self.__register_control)

        self.__search_for_controls()



    #
    # Returns whether the given path has a control.
    #
    def __is_control(self, path):

        # is this test sufficient?
        return os.path.exists(os.path.join(path, "__init__.py"))



    #
    # Returns a list of all controls in the given repository.
    #
    def __find_controls(self, path):

        out = []
        if (not os.path.isdir(path)): return out

        files = os.listdir(path)
        for f in files:
            fpath = os.path.join(path, f)
            if (os.path.isdir(fpath)):
                if (self.__is_control(fpath)): out.append(fpath)
                else:
                    out += self.__find_controls(fpath)

        return out


    #
    # Registers the given control. Registering a control requires us to
    # actually load the control, so this is a critical phase where we have to
    # be careful about malware.
    #
    def __register_control(self, ctrl):

        items = []

        # it's more secure to use a separate process here
        cmd = os.path.join(HOME, "ctrlinfo")
        fail, out = commands.getstatusoutput("%s %s" % (cmd, ctrl))

        if (fail):
            log("Warning: \"%s\" is an invalid control." % ctrl)
            return None

        else:
            log("Registering new control \"%s\"." % ctrl)

        # cut off initial crap; you never know what controls might do during
        # initialization...
        out = out[out.find("PATH:"):]

        for line in out.splitlines():
            if (":" in line):
                key, value = line.split(":")
                value = vfs.unescape_path(value)
            else:
                key = value = ""

            if (not value in self.__registry):
                self.__registry[value] = []

            items.append((key, value))

        return items


    #
    # Searches for new controls.
    #
    def __search_for_controls(self):

        self.__mdreg.scan_repositories()

        self.__registry = {}
        
        # for all items
        for item in self.__mdreg.get_item_list():
            # go through all key-value pairs
            for k, v in self.__mdreg.get_item(item):
                # being only interested in the IDs
                if (k in ("ID1", "ID2")):
                    # register every single ID
                    for iface in v.split(" "):
                        
                        # add two references to the control to the registry
                        # a short one without the ID part and the long (traditional)
                        # one
                        short_iface = iface.split(':')[0]
                        if short_iface not in self.__registry:
                            self.__registry[short_iface] = []
                            self.__registry[iface] = []

                        elif (not iface in self.__registry):
                            self.__registry[iface] = []
                        
                        self.__registry[iface].append(item)
                        self.__registry[short_iface].append(item)
                        


    #
    # Returns a control matching the given interface.
    #
    def get_control(self, iface, second_try = False):

        candidates = self.__registry.get(iface, [])
        for i in candidates:
            if (os.path.isdir(i)): return i

        if (not second_try):
            # search for new controls and give it a second try
            self.__search_for_controls()
            return self.get_control(iface, True)

        else:
            return ""
