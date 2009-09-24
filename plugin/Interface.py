import Permission
from main import _

import types


class Interface(object):

    """Abstract base class for interfaces."""


    def __get_members(impl):

        """Simply returns all members found in a class."""

        return [ (name, member) for name, member in impl.__dict__.items() ]

    __get_members = staticmethod(__get_members)



    def get_properties(iface):
        
        """Returns a list of the properties of the given implementation."""

        return [ (n, p) for n, p in Interface.__get_members(iface)
                 if (type(p) == property) ]

    get_properties = staticmethod(get_properties)



    def get_methods(iface):
        
        """Returns a list of the methods of the given implementation."""

        return [ (n, "") for n, m in Interface.__get_members(iface)
                if (type(m) == types.FunctionType) ] # or MethodType ?

    get_methods = staticmethod(get_methods)



    def get_permissions(iface):

        """Returns a list of the permissions of the properties."""

        perms = [ (n, perm) for n, perm in Interface.__get_members(iface)
                  if (isinstance(perm, Permission._Permission)) ]

        return perms
    
    get_permissions = staticmethod(get_permissions)



    def get_taz_style_id(iface):
        """
          Computes and returns the interface in the wrong way for maintaining
          backwards compatibility.
        """

        import utils

        name = iface.__name__

        try:
            import hashlib
            ash = hashlib.md5(name + ":").hexdigest()
        except:
            import md5
            ash = md5.new(name + ":").hexdigest()

        # encode it in base36 to get shorter ID
        ash = utils.radix( int(ash, 16), 36 )
        # ID have to be 25 char long
        ash = '0' * (25 - len(ash)) + ash
        assert (len(ash) == 25)
        return ("%s:%s" % (name, ash))

    get_taz_style_id = staticmethod(get_taz_style_id)
        


    def get_id(iface):

        """Returns the unique identifier of the given interface."""

        # the algorithm is simple:
        # build a string containing the class name and a sorted list of the
        # properties and return the MD5 fingerprint of it
        import hashlib
        import utils

        name = iface.__name__
        items1 = Interface.get_permissions(iface)
        items1.sort()
        items2 = Interface.get_methods(iface)
        items2.sort()

        tmp = ["%s:%s" % (k, v) for k, v in items1 + items2]
        tmp = "%s:%s" % (name, ",".join(tmp))

        try:
            import hashlib
            ash = hashlib.md5(tmp).hexdigest()
        except:
            import md5
            ash = md5.new(tmp).hexdigest()

        # encode it in base36 to get shorter ID
        ash = utils.radix( int(ash, 16), 36 )
        # ID have to be 25 char long
        ash = '0' * (25 - len(ash)) + ash

        assert (len(ash) == 25)

        # the "-2" suffix is for marking the ID as rev 2
        iface_id = "%s:%s-2" % (name, ash)
        return iface_id

    get_id = staticmethod(get_id)


    def get_rev_of_id(ident):

        """Returns the revision of the format in which the ID is computed."""

        if (ident[-2] != "-"): return "1"
        else: return ident[-1]

    get_rev_of_id = staticmethod(get_rev_of_id)



    def get_interfaces(impl):

        """Returns the interfaces implemented by the given class"""

        return [ c for c in impl.mro()
                 if issubclass(c, Interface) and not c in (Interface, impl) ]

    get_interfaces = staticmethod(get_interfaces)



    def assert_interfaces(impl):
        """Static method for asserting that the interfaces are implemented
           properly in the given class. Throws exceptions otherwise."""

        # find the implemented properties
        impl_props = dict(impl.get_properties())

        # find the implemented methods
        impl_meths = dict(impl.get_methods())

        # check all interfaces
        for iface in Interface.get_interfaces(impl):

            # check properties
            required = iface.get_permissions()
            for name, perm in required:
                if name not in impl_props:
                    raise NotImplementedError("Missing implementation for "
                                              "%s.%s" % (iface.__name__, name))

                # check if the property's mode is according to the interfaces
                if (perm != Permission.Permission(implemented[name])):
                    raise NotImplementedError("Broken implementation for "
                                      "%s.%s" % (iface.__name__, name))
            #end for

            # check methods
            required = iface.get_methods()
            for name, meth in required:
                if name not in impl_meths:
                    raise NotImplementedError("Missing implementation for "
                                              "%s.%s" % (iface.__name__, name))
            #end for

        #end for

    assert_interfaces = staticmethod(assert_interfaces)



    def text_describe(impl):

        """Returns a description of the interfaces of the given class."""

        textlist = []
        interfaces = Interface.get_interfaces(impl)

        for i in interfaces:

            out = ""

            ident = Interface.get_id(i)

            out += ident + '\n\n'

            for key in dir(i):

                value = impl.__dict__.get(key)
                if (not value): continue

                if (isinstance(value, property)):
                    out += "  "
                    out += key.ljust(25)
                    perm = str(Permission.Permission(value)).ljust(4)
                    out += perm
                    out += "%s \n" % (value.__doc__ or _("no description"), )

            out += "\n"

            textlist.append(out)

        return ''.join(textlist)

    text_describe = staticmethod(text_describe)


    def gui_describe(impl):

        guilist = []
        interfaces = Interface.get_interfaces(impl)

        for i in interfaces:

            items = []
            
            for key in dir(i):

                value = impl.__dict__.get(key)
                if (not value): continue

                if (isinstance(value, property)):
                    items.append((key, str(Permission.Permission(value)),
                                    value.__doc__ or _("no description")))

            guilist.append( (Interface.get_id(i), items) )

        return guilist


    gui_describe = staticmethod(gui_describe)

