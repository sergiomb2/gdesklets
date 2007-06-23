from ControlFactory import ControlFactory
from utils.TargetSettings import TargetSettings
from display.Display import Display
from utils.datatypes import *
from utils import dialog
from utils import vfs

from xml import sax

import os
import sys


_STATE_NONE = -1
_STATE_DISPLAY = 0
_STATE_META = 1
_STATE_SCRIPT = 2
_STATE_PREFS = 3
_STATE_SENSOR = 4  # deprecated
_STATE_CONTROL = 5

_SENSOR_CONTROL = "ISensor:2peqs3czo5mlrv5ibwwkn5dqc"


#
# Class for creating Displays from XML data.
#
class _DisplayFactory(sax.handler.ContentHandler):

    def __init__(self):

        # the current state of the parser
        self.__state = [_STATE_NONE]

        # a stack of (tagname, attributes) pairs for remembering the nesting
        # of elements
        self.__nesting_stack = []

        # a stack of (type, settings, children) tuples to remember the children
        # of elements; children is a list of (type, settings, children) tuples
        self.__children_stack = [[]]

        # a list of the sensors for the display
        self.__sensors = []

        # the config items of the display
        self.__config_items = []

        self.__path = ""
        self.__scripts = []
        self.__script = ""
        self.__id = ""
        self.__control_factory = ControlFactory()
        self.__prefs_callback = None
        self.__metadata = {}

        sax.handler.ContentHandler.__init__(self)



    def __reset(self):

        self.__scripts = []
        self.__config_items = []
        self.__children_stack = [[]]
        self.__nesting_stack = []
        self.__sensors = []
        self.__prefs_callback = None
        self.__metadata = {}


    #
    # Parses the given XML data and returns a new Display object.
    #
    def create_display(self, ident, data, dspfile):

        dsp = Display(ident, dspfile)

        self.__reset()
        self.__id = ident
        self.__path = os.path.dirname(dspfile)
        self.__filename = dspfile

        # parse display data
        try:
            sax.parseString(data, self)

        except sax._exceptions.SAXParseException, sax_exc:
            raise UserError(_("XML parse error"),
                            _("This .display file has invalid XML syntax."),
                            code = data, lineno = sax_exc.getLineNumber())

        # add the sensor controls
        for ident, sensorctrl in self.__sensors:
            dsp.add_sensor(ident, sensorctrl)

        # add the children and configure
        childtype, settings, children = self.__children_stack.pop()[0]
        dsp.set_content(childtype, settings, children)

        # set some meta data if available
        preview = self.__metadata.get("preview", "")
        name = self.__metadata.get("name", "")
        version = self.__metadata.get("version", "")
        author = self.__metadata.get("author", "")
        dsp.set_metadata(preview = preview,
                         name = name,
                         version = version,
                         author = author)
        dsp.build_configurator(self.__config_items)

        # add scriptlets
        for script, filename in self.__scripts:
            dsp.add_scriptlet(script, filename)

        self.__reset()

        return dsp



    #
    # Creates a TargetSettings object from the given Attributes object.
    #
    def __create_settings(self, attrs):

        settings = TargetSettings()
        for key, value in attrs.items():
            settings.set(key, value)

        return settings



    def startElement(self, name, attrs):

        attrs_dict = {}
        attrs_dict.update(attrs)

        if (name == "display"):
            self.__state.append(_STATE_DISPLAY)

        elif (name == "prefs"):
            # support a global prefs callback
            self.__prefs_callback = attrs.get("callback", None)
            self.__state.append(_STATE_PREFS)

        elif (name == "meta"):
            self.__state.append(_STATE_META)

        elif (name == "sensor"):
            log("Deprecation: Sensors are deprecated since v0.30.\n"
                "Please consider using controls and inline scripts.")
            self.__state.append(_STATE_SENSOR)

        elif (name == "control"):
            self.__state.append(_STATE_CONTROL)

        elif (name == "script"):
            self.__state.append(_STATE_SCRIPT)
            self.__script = ""

        if (self.__state[-1] == _STATE_DISPLAY):
            self.__children_stack.append([])

        # remember everything for later
        self.__nesting_stack.append((name, attrs_dict))



    def endElement(self, name):

        oname, attrs = self.__nesting_stack.pop()
        state = self.__state[-1]
        if (not name == oname):
            # nesting errors in XML are detected by the SAX parser; if we
            # get here, it means our parser is buggy, not the XML input
            log("Nesting error: expected %s, got %s." % (oname, name))
            return


        elif (state == _STATE_DISPLAY):
            settings = self.__create_settings(attrs)
            # if there is no ID given, guess a unique one
            ident = attrs.get("id", Display.make_id())
            settings["id"] = ident

            # build the tree of children from bottom up
            children = self.__children_stack.pop()
            self.__children_stack[-1].append((name, settings, children))

        elif (state == _STATE_META):
            self.__metadata = attrs

        elif (state == _STATE_SCRIPT):
            # Some distros ship a broken SAX parser and
            # their users are too lazy to reportbug. (doesn't have __contains__)
            # So we have to use has_key()
            # if ((name == "script") and ("uri" in attrs)):
            if (name == "script" and attrs.has_key("uri")):
                path = attrs["uri"]
                filename = os.path.join(self.__path, path)
                try:
                    self.__script += "\n" + vfs.read_entire_file(filename)
                except:
                    log("File doesn't exist or couldn't be loaded: %s"
                        % (path,))
                    dialog.warning(_("File doesn't exist or couldn't be "
                                     "loaded"),
                                   _("A file which contains a script isn't "
                                     "available for further execution."))
            else:
                filename = self.__filename

            # collect script by script to be able to execute them one by one
            # later; we would get problems with different indentation otherwise
            self.__scripts.append((self.__script, filename))

        # deprecated sensor stuff
        elif (state == _STATE_SENSOR):
            from utils import typeconverter
            ident = attrs["id"]
            moduledata = typeconverter.str2type(TYPE_LIST, attrs["module"])
            module = moduledata[0]
            args = moduledata[1:]
            sensorctrl = self.__control_factory.get_control(_SENSOR_CONTROL)

            if (sensorctrl):
                sensorctrl.sensor = (module, args)
                sensorctrl.config_id = self.__id + ident
                self.__sensors.append((ident, sensorctrl))
            else:
                raise RuntimeError(_("Could not load sensor"))

        elif (state == _STATE_CONTROL):
            ident = attrs["id"]
            interface = attrs["interface"]
            script = "%s = get_control('%s')" \
                     % (ident, interface)
            self.__scripts.append((script, self.__filename))

        elif (state == _STATE_PREFS):
            if (name == "prefs"):
                pass
            else:
                if (name in ("boolean", "color", "enum", "float", "font",
                             "integer", "string", "uri")
                    and not attrs.has_key("bind")):
                    dialog.warning(_("&lt;%s&gt; needs a bind attribute") % \
                                                                      (name,),
                                   _("The &lt;prefs&gt; section of this "
                                     "desklet file is broken."))
                    raise AttributeError("<%s> needs a bind attribute" % \
                                                                      (name,))

                # use global prefs callback if no callback was given
                if (self.__prefs_callback and not attrs.has_key("callback")):
                    attrs["callback"] = self.__prefs_callback

                self.__config_items.append((name, attrs))


        if (name in ("display", "sensor", "control", "meta",
                     "prefs", "script")):
            self.__state.pop()



    def characters(self, content):

        state = self.__state[-1]
        if (state == _STATE_SCRIPT):
            self.__script += str(content)


_singleton = _DisplayFactory()
def DisplayFactory(): return _singleton
