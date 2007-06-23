from main import _
from utils.HIGDialog import HIGDialog

import gtk


#
# Class for the display configurator. It displays the configurators of the
# sensors of a display.
#
class DisplayConfigurator(HIGDialog):

    def __init__(self, sensorconfigurators):

        HIGDialog.__init__(self, buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.set_property("title", _("Configuration"))

        def destroy(*args): self.destroy()

        self.connect("response", destroy)

        # close functions
        pages = []
        for c in sensorconfigurators:
            if (c):
                lbl = gtk.Label(c.get_name())
                lbl.show()
                pages.append((c, lbl))

        # use a special page when there are no config options
        if (not pages):
            lbl = gtk.Label(_("This desklet is not configurable."))
            lbl.show()
            pages.append((lbl, None))

        # only use the notebook when there are more than one pages
        if (len(pages) == 1):
            self.vbox.add(pages[0][0])
        else:
            align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
            align.show()
            notebook = gtk.Notebook()
            notebook.set_property("border-width", 6)
            notebook.show()
            align.add(notebook)
            self.vbox.pack_start(align, False, False, 0)
            for page, tab in pages:
                notebook.append_page(page, tab)

        self.show()

