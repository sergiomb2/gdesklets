from utils.datatypes import *


class Element(object):
    """
      Base class for elements with typed properties.
      Classes deriving from this base class have to call

        _register_property(name, datatype, setter, getter, default, doc)

      in the constructor. Properties can then be set with

        set_prop(key, value)

      and can be read with

        get_prop(key, value)


      If you don't need any special setter or getter methods, then you can use
      the predefined _setp(key, value) and _getp(key) methods.
    """

    __slots__ = ('__name', '__properties', '__property_handlers',
                 '__ident_counter')

    AUTHORIZED_METHODS = ()

    # counter for unique IDs
    __ident_counter = 0


    def __init__(self, name):

        # name of the element
        self.__name = name

        # values of the properties
        self.__properties = {}

        # table: property name -> (setter, getter, datatype, doc)
        self.__property_handlers = {}


        new_id = "id%d" % self.__ident_counter
        self.__ident_counter += 1
        self._register_property("id", TYPE_STRING, self._setp, self._getp,
                                new_id, doc = "Unique identifier")



    #
    # Registers the given property with the given setter and getter methods.
    #
    def _register_property(self, name, datatype, setter, getter,
                           default = None, doc = ""):

        self.__property_handlers[name] = (setter, getter, datatype, doc)
        self._setp(name, default)



    #
    # Sets the given property as a string.
    #
    def set_prop_from_string(self, key, value):

        value = str(value)  # to stay compatible with sensors :(
        key = key.replace("_", "-")
        try:
            datatype = self.get_datatype_of_property(key)
        except KeyError:
            datatype = TYPE_ANY

        from utils import typeconverter
        self.set_prop(key, typeconverter.str2type(datatype, value))



    #
    # Sets the given property.
    #
    def set_prop(self, key, value):

        key = key.replace("_", "-")
        try:
            setter = self.__property_handlers[key][0]
            datatype = self.__property_handlers[key][2]

        except KeyError:
            raise UserError(_("No such property: %s") % key,
                            _("The element <b>%s</b> does not have the "
                              "<b>%s</b> property.") % (self.__name, key))
        
        if (not setter):
            raise UserError(_("Permission Error"),
                           _("The property <b>%s</b> of element <b>%s</b> "
                             "is not writable.") % (key, self.__name))
        
        elif (dtype_check(datatype, value)):
            setter(key, value)

        else:
            actual_type = dtype_guess(value)
            raise UserError(_("Type Error"),
                           _("The property <b>%s</b> of element <b>%s</b> "
                             "got a value of wrong type.\n"
                             "Expected <b>%s</b>, but got <b>%s</b>."
                             % (key, self.__name, datatype[0],
                                actual_type[0])))



    #
    # Returns the value of the given property.
    #
    def get_prop(self, key):

        key = key.replace("_", "-")
        try:
            getter = self.__property_handlers[key] [1]
        except KeyError:
            raise KeyError("Error: No such property: %s" % key)

        if (not getter):
            raise UserError(_("Permission Error"),
                           _("The property <b>%s</b> of element <b>%s</b> "
                             "is not readable.") % (key, self.__name))
        
        else:
            return getter(key)



    #
    # Returns the datatype of the given property.
    #
    def get_datatype_of_property(self, prop):

        # we intentionally don't catch the KeyError here
        return self.__property_handlers[prop][2]



    #
    # Returns the documentation string of the given property.
    #
    def get_doc_of_property(self, prop):

        try:
            doc = self.__property_handlers[prop][3]
        except:
            return ""

        return doc



    #
    # Returns a list of the names of all available properties.
    #
    def get_props(self): return self.__property_handlers.keys()



    #
    # Generic setter and getter methods for properties.
    #
    def _setp(self, key, value): self.__properties[key] = value
    def _getp(self, key): return self.__properties[key]


    #
    # Returns the element's name
    #
    def get_name(self): return self.__name
