import gtk


#
# Class for the configuration widgets of a sensor.
#
class SensorConfigurator(gtk.VBox):

    CHANGE_ENTRY = 0
    CHANGE_OPTION = 1
    CHANGE_SPIN = 2
    CHANGE_CHECKBOX = 3
    CHANGE_FONT = 4
    CHANGE_COLOR = 5
    CHANGE_FILE = 6


    def __init__(self, set_config, get_config):

        # functions for setting / getting configuration values of the sensor
        self.__set_config = set_config
        self.__get_config = get_config

        # name of the configurator
        self.__name = ""

        # the number of widget lines
        self.__lines = 0


        gtk.VBox.__init__(self)
        self.set_border_width(12)
        self.show()

        self.__table = gtk.Table(1, 2)
        self.__table.show()
        self.add(self.__table)

        self.__tooltips = gtk.Tooltips()

        self.callbacks = []


    #
    # Reacts on changing a setting.
    #
    def __on_change(self, src, *args):

        property, mode = args[-2:]
        args = args[:-2]

        if (mode == self.CHANGE_ENTRY):
            value = src.get_text()

        elif (mode == self.CHANGE_OPTION):
            items = args[0]
            value = items[src.get_active()]

        elif (mode == self.CHANGE_CHECKBOX):
            value = src.get_active()

        elif (mode == self.CHANGE_SPIN):
            value = src.get_value_as_int()

        elif (mode == self.CHANGE_FONT):
            value = src.get_font_name()

        elif (mode == self.CHANGE_COLOR):
            color = src.get_color()
            value = "#%02X%02X%02X" % (color.red >> 8, color.green >> 8,
                                       color.blue >> 8)

        self.__set_config(property, value)


    #
    # Sets/returns the name of this configurator. That name will appear in the
    # notebook tab.
    #
    def set_name(self, name): self.__name = name
    def get_name(self): return self.__name



    #
    # Adds a line of widgets to the configurator. The line can be indented.
    #
    def __add_line(self, indent, w1, w2 = None):

        self.__lines += 1
        self.__table.resize(self.__lines, 2)

        if (indent): x, y = 12, 3
        else: x, y = 0, 3

        if (w2):
            self.__table.attach(w1, 0, 1, self.__lines - 1, self.__lines,
                                gtk.FILL, 0, x, y)
            self.__table.attach(w2, 1, 2, self.__lines - 1, self.__lines,
                                gtk.EXPAND | gtk.FILL, 0, 0, y)

        else:
            self.__table.attach(w1, 0, 2, self.__lines - 1, self.__lines,
                                gtk.EXPAND | gtk.FILL, 0, x, y)



    def add_title(self, label):

        lbl = gtk.Label("")
        lbl.set_markup("<b>" + label + "</b>")
        lbl.show()
        align = gtk.Alignment()
        align.show()
        align.add(lbl)

        self.__add_line(0, align)



    def add_checkbox(self, label, property, help):

        check = gtk.CheckButton(label)
        check.show()

        self.__tooltips.set_tip(check, help)
        self.__add_line(1, check)

        value = self.__get_config(property)
        check.set_active(value)
        check.connect("toggled", self.__on_change, property,
                      self.CHANGE_CHECKBOX)



    def add_entry(self, label, property, help, passwd = 0):

        lbl = gtk.Label(label)
        lbl.show()
        entry = gtk.Entry()
        entry.show()
        align = gtk.Alignment()
        align.show()
        align.add(lbl)

        if (passwd):
            entry.set_visibility(False)
            entry.set_invisible_char(unichr(0x2022))

        self.__tooltips.set_tip(entry, help)
        self.__add_line(1, align, entry)

        value = self.__get_config(property)
        entry.set_text(value)
        entry.connect("changed", self.__on_change, property,
                      self.CHANGE_ENTRY)



    def add_spin(self, label, property, help, low, up):

        lbl = gtk.Label(label)
        lbl.show()

        align = gtk.Alignment()
        align.show()
        align.add(lbl)

        adjustment = gtk.Adjustment(0, int(low), int(up), 1, 1, 0)
        spin_button = gtk.SpinButton(adjustment, 1, 0)
        spin_button.set_numeric(True)
        spin_button.show()

        value = self.__get_config(property)

        self.__tooltips.set_tip(spin_button, help)
        self.__add_line(1, align, spin_button)

        spin_button.set_value(value)
        spin_button.connect("value-changed", self.__on_change, property,
                            self.CHANGE_SPIN)



    def add_option(self, label, property, help, options):

        lbl = gtk.Label(label)
        lbl.show()

        align = gtk.Alignment()
        align.show()
        align.add(lbl)

        value = self.__get_config(property)

        optmenu = gtk.combo_box_new_text()
        optmenu.show()
        items = []
        cnt = 0
        index = 0
        for k, v in options:
            optmenu.append_text(k)
            items.append(v)
            if (v == value): index = cnt
            cnt += 1
        #end for
        optmenu.set_active(index)
        optmenu.connect("changed", self.__on_change, items, property,
                        self.CHANGE_OPTION)

        self.__tooltips.set_tip(optmenu, help)
        self.__add_line(1, align, optmenu)



    def add_font_selector(self, label, property, help):

        lbl = gtk.Label(label)
        lbl.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(lbl)

        btn = gtk.FontButton()
        btn.set_use_font(True)
        btn.set_use_size(False)
        btn.set_show_style(True)
        btn.set_show_size(True)
        btn.show()
        btn.connect("font-set", self.__on_change, property,
                     self.CHANGE_FONT)

        font = self.__get_config(property)
        btn.set_font_name(font)

        self.__tooltips.set_tip(btn, help)
        self.__add_line(1, align, btn)



    def add_color_selector(self, label, property, help):

        lbl = gtk.Label(label)
        lbl.show()
        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.show()
        align.add(lbl)

        btn = gtk.ColorButton()
        btn.set_use_alpha(True)
        btn.show()
        print property
        btn.connect("color-set", self.__on_change, property, self.CHANGE_COLOR)

        colorname = self.__get_config(property)
        color = gtk.gdk.color_parse(colorname)

        btn.set_color(color)

        self.__tooltips.set_tip(btn, help)
        self.__add_line(1, align, btn)



    def add_file_selector(self, label, property, help):

        def open_filedialog(self, on_ok, entry):
            def fd_hide(src, fselector): fselector.destroy()
            d = gtk.FileSelection()
            d.show()
            d.ok_button.connect("clicked", on_ok, d, entry)
            d.cancel_button.connect("clicked", fd_hide, d)

        def on_ok(src, fselector, entry):
            fname = fselector.get_filename()
            entry.set_text(fname)
            fselector.destroy()

        lbl = gtk.Label(label)
        lbl.show()
        align = gtk.Alignment()
        align.show()
        align.add(lbl)

        hbox = gtk.HBox()
        hbox.show()
        entry = gtk.Entry()
        entry.show()
        hbox.pack_start(entry, True, True, 0)

        btn = gtk.Button(stock = gtk.STOCK_OPEN)
        btn.show()
        hbox.pack_end(btn, True, True, 4)

        btn.connect("clicked", open_filedialog, on_ok, entry)

        value = self.__get_config(property)
        entry.set_text(value)
        entry.connect("changed", self.__on_change, property,
                      self.CHANGE_ENTRY)

        self.__tooltips.set_tip(entry, help)
        self.__tooltips.set_tip(btn, help)
        self.__add_line(1, align, hbox)

    #
    # Adds a function to be called when the user closes the configurator
    #
    def add_close_callback(self, fct, args=None):

        self.callbacks.append( (fct, args) )
