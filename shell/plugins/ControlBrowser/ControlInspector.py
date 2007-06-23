import gtk

from plugin.Interface import Interface
from utils.HIGDialog import HIGDialog


#
# Dialog for inspecting controls.
#
class ControlInspector(HIGDialog):

    def __init__(self, ctrlclass):

        HIGDialog.__init__(self, buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        name = ctrlclass.__name__
        self.set_property("title", _("%s Control") % (name))

        align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
        align.set_property("border-width", 6)
        self.__scrollw = gtk.ScrolledWindow()
        align.add(self.__scrollw)

        self.__label = gtk.Label()
        self.__label.set_property("selectable", True)

        self.vbox.pack_start(align, False, False, 0)
        self.vbox.pack_start(self.__label, False, False, 0)

        # list the interfaces and their descriptions
        texts = Interface.gui_describe(ctrlclass)

        # create the listview now, with the content
        self.__create_listview(texts)

        def f(*args): self.destroy()
        self.connect("response", f)

        self.vbox.show_all()


    def __create_listview(self, texts):

        self.__label.set_property("label", texts[0][0])

        import gobject, pango

        treemodel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                  gobject.TYPE_STRING, gobject.TYPE_STRING)
        treeview = gtk.TreeView(treemodel)

        textrenderer0 = gtk.CellRendererText()
        textrenderer0.set_property("weight", pango.WEIGHT_BOLD)
        textrenderer1 = gtk.CellRendererText()

        column0 = gtk.TreeViewColumn(_("Interface Name"), textrenderer0)
        column0.add_attribute(textrenderer0, "text", 0)
        treeview.append_column(column0)
        column1 = gtk.TreeViewColumn(_("Property Name"), textrenderer1)
        column1.add_attribute(textrenderer1, "text", 1)
        treeview.append_column(column1)
        column2 = gtk.TreeViewColumn(_("Property Access"), textrenderer1)
        column2.add_attribute(textrenderer1, "text", 2)
        treeview.append_column(column2)
        column3 = gtk.TreeViewColumn(_("Property Description"), textrenderer1)
        column3.add_attribute(textrenderer1, "text", 3)
        treeview.append_column(column3)

        for (iface, items) in texts:

            myiter = treemodel.insert_before(None, None,
                                             (iface.split(":")[0], None, None,
                                              None))

            for name, access, description in items:
                treemodel.insert_before(myiter, None,
                                        (None, name, access, description))

        treeview.expand_all()
        w, h = treeview.size_request()
        self.__scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__scrollw.set_size_request(max(w + 20, 600), min(h, 400))
        self.__scrollw.add(treeview)

