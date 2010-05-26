"""
Class for a simple mini DOM.

This class takes an SVG string at construction time and then provides a way to
modify element properties in the DOM tree.
The DOM object can be serialized to a XML string at any time.
"""

from xml import sax
from error import UserError    

class DOM(sax.handler.ContentHandler):

    def __init__(self, xml):

        self.__dom = None
        self.__node_stack = []
        self.__current_node = None
        self.__current_chars = ""
        self.__id_table = {}

        sax.handler.ContentHandler.__init__(self)

        # silly PyXML fails for standalone="no" documents without net access,
        # so rip that out
        xml = self.__modify_standalone(xml)

        try:
            sax.parseString(xml, self)
        except sax._exceptions.SAXParseException, exc:
            raise UserError(_("XML parse error"),
                            _("An invalid graphics code was loaded into a "
                              "canvas."),
                            code = xml, lineno = exc.getLineNumber())
        except:
            return

        self.__dom.set_id_table(self.__id_table)


    #
    # Rips out a standalone="yes" attribute if it's set. We don't need and don't
    # want it for SVGs.
    #
    def __modify_standalone(self, xml):

        index1 = xml.find("<")

        if (xml[index1 + 1] != "?"):
            # no header; nothing to do
            return xml

        index2 = xml.find("?>")
        header = xml[index1:index2]
        index3 = header.find("standalone")

        if (index3 == -1):
            # no "standalone setting; add one
            return xml[:index1] + " standalone='yes'" + xml[index2:]

        state = 0
        index4 = index3 + 10
        for c in header[index4:]:
            index4 += 1
            if (c in ("\"", "'")): state += 1
            if (state == 2): break

        if ("no" in header.lower()[index3:index4]):
            # replace with "yes"
            xml = xml[:index1 + index3] + \
        xml[index1 + index3:index1 + index4].lower().replace("no", "yes") + \
                  xml[index1 + index4:]
            
        return xml
    

    def get_root(self): return self.__dom
    

    def startElement(self, name, attrs):

        parent = self.__current_node
        self.__current_node = _DOMNode(name)
        self.__current_chars = ""
        for key, value in attrs.items():
            self.__current_node[key] = value

        if (parent): parent.add_child(self.__current_node)
        else:
            # we insert an empty <g> node here; it can be used later if needed
            # TODO: not here; this is meant to be a generic DOM
            self.__dom = self.__current_node
            new_node = _DOMNode("g")
            self.__dom.add_child(new_node)
            self.__current_node = new_node

        if ("id" in attrs.keys()):
            self.__id_table[attrs["id"]] = self.__current_node

        self.__node_stack.append(self.__current_node)
        

    def endElement(self, name):

        if (self.__current_chars):
            self.__current_node["PCDATA"] = self.__current_chars

        self.__node_stack.pop(-1)
        if (self.__node_stack):
            self.__current_node = self.__node_stack[-1]


    def characters(self, content):

        self.__current_chars += content



#
# Class for nodes of the DOM tree.
#
class _DOMNode:

    def __init__(self, name):

        self.__name = name
        self.__attrs = {}
        self.__children = []
        self.__update_handler = None
        self.__id_table = {}


    #
    # Sets the ID table for quickly accessing a node by its ID.
    #
    def set_id_table(self, table): self.__id_table = table


    #
    # Returns whether the given key exists.
    #
    def has_key(self, key): return (key in self.__attrs)


    #
    # Returns the node with the given ID.
    #
    def get(self, ident):

        try:
            return self.__id_table[ident]
        except KeyError:
            raise UserError(_("No such element: %s") % ident,
                           _("The element with ID <b>%s</b> does not "
                             "exist in the SVG image.") % ident)


    #
    # Sets the handler for updating the tree.
    #
    def set_update_handler(self, handler):

        self.__update_handler = handler

    #
    # Updates the tree.
    #
    def update(self):

        if (self.__update_handler): self.__update_handler()
        

    def add_child(self, child): self.__children.append(child)
    def get_children(self): return self.__children[:]


    def __getitem__(self, key):

        try:
            return self.__attrs[key]
        except KeyError:
            raise UserError(_("No such property: %s") % key,
                           _("The SVG element <b>%s</b> does not have the "
                             "<b>%s</b> property.") % (self.__name, key))
        
    def __setitem__(self, key, value): self.__attrs[key] = value


    #
    # Returns a XML representation of this node.
    #
    def __str__(self):

        attrs = [ "%s=\"%s\"" % (k, v) for k, v in self.__attrs.items() ]
        attrs = " ".join(attrs)
        children = [ str(c) for c in self.get_children() ]
        children = "\n".join(children)
        contents = self.__attrs.get("PCDATA", "")
        contents += children
        if (contents):
            out = "<%s %s>%s</%s>" % (self.__name, attrs, contents, self.__name)
        else:
            out = "<%s %s/>" % (self.__name, attrs)

        return out
