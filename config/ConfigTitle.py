from ConfigWidget import ConfigWidget

import gtk

class ConfigTitle(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        ConfigWidget.__init__(self, name, getter, setter, caller)


    def get_widgets(self):

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 1.0, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        return (align,)


    def _set_label(self, value): self.__label.set_markup("<b>" + value + "</b>")
