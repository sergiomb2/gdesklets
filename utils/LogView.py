import gtk
import pango
import textwrap


# attributes for rendering text
_ATTR_TITLE =      {"weight": pango.WEIGHT_BOLD,
                    "font": "Mono"}
_ATTR_DEBUG =      {"foreground": "white",
                    "background": "red",
                    "weight": pango.WEIGHT_BOLD,
                    "underline": pango.UNDERLINE_SINGLE,
                    "font": "Mono"}
_ATTR_DEPRECATED = {"foreground": "black",
                    "background": "yellow",
                    "weight": pango.WEIGHT_BOLD,
                    "font": "Mono"}
_ATTR_ERROR =      {"foreground": "darkred",
                    "background": "white",
                    "weight": pango.WEIGHT_BOLD,
                    "font": "Mono"}
_ATTR_INFO =       {"foreground": "black",
                    "background": "green",
                    "weight": pango.WEIGHT_BOLD,
                    "font": "Mono"}
_ATTR_WARN =       {"foreground": "black",
                    "background": "orange",
                    "weight": pango.WEIGHT_BOLD,
                    "font": "Mono"}
_ATTR_CODE =       {"foreground": "navy",
                    "background": "white",
                    "font": "Mono"}
_ATTR_BAD_CODE =   {"foreground": "navy",
                    "background": "#ff7173",
                    "font": "Mono"}
_ATTR_NORMAL =     {"foreground": "black",
                    "background": "white"}


#
# A specialized TextView widget for formatting log and error messages with
# markups.
#
class LogView(gtk.TextView):

    def __init__(self):

        self.__wrap_at = 85  # 85 to have line numbers before code lines

        gtk.TextView.__init__(self)
        self.set_editable(False)
        self.set_wrap_mode(gtk.WRAP_NONE)



    def append(self, data):

        """ Adds data to the buffer """

        lines = data.splitlines()
        for line in lines:
            text, attrs = self.__markup(line)
            for chunk in textwrap.wrap(text, self.__wrap_at):
                chunk = chunk.ljust(self.__wrap_at) + "\n"

                end_iter = self.get_buffer().get_end_iter()
                tag = self.get_buffer().create_tag(None, **attrs)
                self.get_buffer().insert_with_tags(end_iter, chunk, tag)



    def __markup(self, text):

        """ Analyzes the given text and returns the appropriate attribute. """

        if ("Deprecation" in text):
            return (text, _ATTR_DEPRECATED)
        elif (text.startswith("===")):
            return (text, _ATTR_TITLE)
        elif (text.startswith("[EXC]")):
            return (text[5:], _ATTR_ERROR)
        elif (text.startswith("[DSC]")):
            return (text[5:], _ATTR_INFO)
        elif ("Info:" in text):
            return (text, _ATTR_INFO)
        elif ("Debug:" in text):
            return (text, _ATTR_DEBUG)
        elif ("Warning:" in text):
            return (text, _ATTR_WARN)
        elif (text.startswith("[---]")):
            return (text[5:], _ATTR_CODE)
        elif (text.startswith("[ERR]")):
            return (text[5:], _ATTR_BAD_CODE)
        else:
            return (text, _ATTR_NORMAL)
