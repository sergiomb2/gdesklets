from ConfigWidget import ConfigWidget
from utils.datatypes import *
from layout import Unit

import gtk

class ConfigUnit(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__lock = False

        self.__units = []
        self.__prev_unit = Unit.UNIT_PX


        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("min", TYPE_FLOAT, self._setp_lhd,
                                self._getp, 0.0, doc = "Lower bound")
        self._register_property("max", TYPE_FLOAT, self._setp_lhd,
                                self._getp, 9999.0, doc = "Upper bound")
        self._register_property("digits", TYPE_INT, self._setp_lhd,
                                self._getp, 2,
                                doc = "Numbers of decimal digits")
        self._register_property("increment", TYPE_FLOAT, self._setp_increment,
                                self._getp, 1, doc = "Size of increments")
        self._register_property("value", TYPE_UNIT, self._setp_value,
                                self._getp, Unit.ZERO, doc = "Value")



    def get_widgets(self):

        low = self.get_prop("min")
        high = self.get_prop("max")
        digits = self.get_prop("digits")

        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        box = gtk.HBox(spacing = 6)
        box.show()

        adjustment = gtk.Adjustment(0, -0xffffff, 0xffffff, 1, 1, 0)
        self.__spin_button = gtk.SpinButton(adjustment, 1, digits)
        self.__spin_button.set_numeric(True)
        self.__spin_button.show()
        self.__spin_button.connect("value-changed", self.__on_change)
        box.pack_start(self.__spin_button, True, True)

        self.__optmenu = gtk.combo_box_new_text()
        self.__optmenu.show()
        for unit, name in ((Unit.UNIT_PX, _("pixel")),
                           (Unit.UNIT_PT, _("point")),
                           (Unit.UNIT_CM, _("cm")),
                           (Unit.UNIT_IN, _("inch")),
                           (Unit.UNIT_PERCENT, "%")):
            self.__units.append(unit)
            self.__optmenu.append_text(name)
        #end for
        self.__optmenu.set_active(0)

        self.__optmenu.connect("changed", self.__on_change_unit)
        box.pack_end(self.__optmenu, False, False)

        return (align, box)


    def __on_change(self, src):

        size = self.__spin_button.get_value()
        unit = self.__units[self.__optmenu.get_active()]

        new_value = Unit.Unit(size, unit)
        self._setp("value", new_value)
        self._set_config(Unit.Unit(size, unit))


    def __on_change_unit(self, src):

        if (self.__lock): return
        
        unit = self.__units[src.get_active()]
        value = self.get_prop("value")
        
        if (unit == Unit.UNIT_PX): size = value.as_px()
        elif (unit == Unit.UNIT_PT): size = value.as_pt()
        elif (unit == Unit.UNIT_CM): size = value.as_cm()
        elif (unit == Unit.UNIT_IN): size = value.as_in()
        elif (unit == Unit.UNIT_PERCENT): size = value.as_percent()

        self.__spin_button.set_value(size)


    def _set_enabled(self, value): self.__spin_button.set_sensitive(value)
    def _set_label(self, value): self.__label.set_text(value)


    def _setp_lhd(self, key, value):

        low, high = self.__spin_button.get_range()
        if (key == "min"):
            self.__spin_button.set_range(value, high)
        elif (key == "max"):
            self.__spin_button.set_range(low, value)
        elif (key == "digits"):
            self.__spin_button.set_digits(value)

        self._setp(key, value)


    def _setp_increment(self, key, value):

        self.__spin_button.set_increments(value, value * 10);
        self._setp(key, value)



    def _setp_value(self, key, value):

        unit = value.get_unit()
        if (unit == Unit.UNIT_PX): size = value.as_px()
        elif (unit == Unit.UNIT_PT): size = value.as_pt()
        elif (unit == Unit.UNIT_CM): size = value.as_cm()
        elif (unit == Unit.UNIT_IN): size = value.as_in()
        elif (unit == Unit.UNIT_PERCENT): size = value.as_percent()

        self.__lock = True
        self.__optmenu.set_active(self.__units.index(unit))
        self.__spin_button.set_value(size)
        self.__lock = False
        self._setp(key, value)
