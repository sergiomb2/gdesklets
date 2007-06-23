import sys
from xml.parsers import expat


class ControlWriter(object):

    __INDENT = " " * 4
    __PRIVATE = "%s%sself.__" % (__INDENT, __INDENT)
    __INIT = "%sdef __init__(self):\n\n%s%sControl.__init__(self)\n\n" % \
        (__INDENT, __INDENT, __INDENT)
    __IFACE = "from libdesklets import Interface, Permission\n\nclass I"
    __CONTROL = "from libdesklets.controls import Control\nfrom "

    def __init__(self, filename):

        self.__imports = ""
        self.__attributes = ""
        self.__attribute_list = {}
        self.__methods = ""
        self.__method_list = {}
        self.__iface_name = ""
        self.__interface_string = ""
        self.__control_string = ""
 
        self.__parser = expat.ParserCreate()
        self.__parser.StartElementHandler = self.__start_element
        self.__parser.EndElementHandler = self.__end_element
        self.__parser.CharacterDataHandler = self.__char_data

        self.__parse_file(filename)


    def __parse_file(self, filename):

        fd = None
        try:
            fd = open(filename, "r")
        except IOError, exc:
            print exc

        self.__parser.ParseFile(fd)




    def __start_element(self, name, attrs):

        if (name == "interface"):
            derived = ""
            if ("derived" in attrs and attrs["derived"]):
                derived = ", %s" % attrs["derived"]
            if ("name" in attrs and not attrs["name"] == ""):
                self.__iface_name = attrs["name"]
                self.__interface_string += "%s%s(Interface%s):\n\n" % \
                    (self.__IFACE, attrs["name"], derived)
            else:
                print "You need to provide an interface name!"
                sys.exit(1)
        
        elif (name == "import"):
            if ("from" in attrs and not attrs["from"] == ""):
                self.__imports += "from %s import " % attrs["from"]
                if ("name" in attrs and not attrs["name"] == ""):
                    self.__imports += "%s\n" % attrs["name"]
                else:
                    print "Import error!"
                    sys.exit(2)
            elif ("name" in attrs and not attrs["name"] == ""):
                self.__imports += "import %s\n" % attrs["name"]

        elif (name == "attribute"):

            if (not "name" in attrs):
                print "You need to provide a name for the attribute!"
                sys.exit(3)
            elif (not "access" in attrs):
                print "You need to provide property access for %s" % \
                    attrs["name"]
                sys.exit(4)
            else:
                access = "READWRITE"
                if (attrs["access"] == "r"): access = "READ"
                elif (attrs["access"] == "w"): access = "WRITE"

                self.__attribute_list[attrs["name"]] = access
                self.__attributes += "\t%s\t\t= Permission.%s\n" % \
                    (attrs["name"], access)

        elif (name == "method"):

            if (not "name" in attrs):
                print "You need to provide a name for the method!"
                sys.exit(3)
            elif (not "access" in attrs):
                print "You need to provide property access for %s" % \
                    attrs["name"]
                sys.exit(4)
            else:
                param = ""
                access = "READWRITE"
                if (attrs["access"] == "r"): access = "READ"
                elif (attrs["access"] == "w"): access = "WRITE"

                if ("param" in attrs and not attrs["param"] == ""):
                    param += attrs["param"]

                self.__method_list[attrs["name"]] = access
                self.__methods += "\t%s\t\t= Permission.%s\n" % \
                    (attrs["name"], access)


    def get_interface_content(self):

        print "%s%s" % (self.__imports, self.__interface_string)
        print "\t### attribute definitions ###\n%s" % self.__attributes
        print "\t### method definitions ###\n%s" % self.__methods


    def get_control_content(self):

        property_str = ""
        method_str = ""
        attrs = "%sI%s import I%s\n\n" % (self.__CONTROL,
                                          self.__iface_name,
                                          self.__iface_name)
        attrs += "class %s(Control, I%s):\n\n" % (self.__iface_name,
                                                  self.__iface_name)
        attrs += self.__INIT
        for item in self.__attribute_list:
            if (self.__attribute_list[item] == "READ"): continue
            attrs += "%s%s\t\t= \"\"\n" % (self.__PRIVATE, item)


        for item in self.__method_list:
            if (self.__method_list[item] == "READ"):
                method_str += "%sdef __get_%s(self):\n\n\tpass" % \
                        (self.__INDENT, item)
                property_str += "%sproperty(__get_%s)\n" % (self.__INDENT, item)
            else:
                method_str += "%sdef __get_%s(self):\n\n\tpass\n\n\n" % \
                        (self.__INDENT, item)
                method_str += "%sdef __set_%s(self, value):\n\n\tpass\n\n\n" % \
                       (self.__INDENT, item)
                property_str += "%sproperty(__get_%s, __set_%s)\n" % \
                        (self.__INDENT, item, item)

        print "%s\n\n%s\n\n\n%s" % (attrs, method_str, property_str)


    def __end_element(self, name):
        pass
        #print 'End element:', name
    def __char_data(self, data):
        pass
        #print 'Character data:', repr(data)


if __name__ == "__main__":
    cw = ControlWriter(sys.argv[1])
    cw.get_interface_content()
    cw.get_control_content()
