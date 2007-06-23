import gtk


class HIGDialog(gtk.Dialog):

    def __init__(self, buttons, type = None, primary = "", secondary = "",
                 self_destroy = True):

        gtk.Dialog.__init__(self, "", None, gtk.WINDOW_TOPLEVEL, buttons)

        # HIG says don't show a separator
        self.set_property("has-separator", False)
        # HIG says don't show up in the taskbar
        self.set_property("skip-taskbar-hint", True)
        # HIG says dialog mustn't be resizable
        self.set_property("resizable", False)
        # HIG says border-width must be set to 6
        self.set_property("border-width", 6)

        self.vbox.set_property("spacing", 12)

        hbox = gtk.HBox()
        hbox.set_property("spacing", 12)
        hbox.set_property("border-width", 6)
        hbox.show()

        if (type):
            icon = gtk.Image()
            icon.set_property("yalign", 0.0)
            icon.set_from_stock(type, gtk.ICON_SIZE_DIALOG)
            icon.show()
            hbox.pack_start(icon, False, False, 0)

            self.vbox.pack_start(hbox, False, False, 0)

        if (primary != "" and secondary != ""):
            # according to the HIG, a dialog message has to look like this
            m = "<span weight=\"bold\" size=\"larger\">%(primary)s</span>\n" \
                "\n" \
                "%(secondary)s" % vars()

            label = gtk.Label()
            label.set_property("use-markup", True)
            label.set_property("selectable", True)
            label.set_property("wrap", True)
            label.set_property("yalign", 0.0)
            label.set_label(m)
            label.show()
            hbox.pack_start(label, False, False, 0)

            # check if the hbox is already added to the vbox
            if (not isinstance(self.vbox.get_children()[0], gtk.HBox)):
               self.vbox.pack_start(hbox, False, False, 0)

        if (self_destroy):
            def f(*args): self.destroy()
            self.connect_after("response", f)

