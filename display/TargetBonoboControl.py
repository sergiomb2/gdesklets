from DisplayTarget import DisplayTarget
from utils.datatypes import *

import gtk


#
# Class for a target that embeds Bonobo controls.
#
class TargetBonoboControl(DisplayTarget):

    def __init__(self, name, parent):

        # the control; you can load a control only once
        self.__control = None

        self.__widget = gtk.HBox()
        self.__widget.show()

        DisplayTarget.__init__(self, name, parent)

        self._register_property("oafiid", TYPE_STRING,
                                self._setp_oafiid, self._getp)


    def get_widget(self): return self.__widget


    def _setp_oafiid(self, key, value):

        import bonobo.ui
        try:
            container = bonobo.ui.Container()
            control = bonobo.ui.Widget(str(value),
                                           container.corba_objref())
            pbag = control.get_control_frame().get_control_property_bag()
            slots = pbag.getKeys("")

            control.show()

            if self.__control:  # we have to remove the previous control
                self.remove( self.__control )

            self.__widget.add(control)
            self.__control = control
            self._setp(key, value)

        except StandardError, exc:
            log("Warning: An error occurred while setting the oafiid:\n%s" \
                % (exc,))

