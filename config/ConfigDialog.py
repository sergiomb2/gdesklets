from ConfigBoolean import ConfigBoolean
from ConfigButton import ConfigButton
from ConfigColor import ConfigColor
from ConfigEnum import ConfigEnum
from ConfigFloat import ConfigFloat
from ConfigFont import ConfigFont
from ConfigInteger import ConfigInteger
from ConfigString import ConfigString
from ConfigTitle import ConfigTitle
from ConfigUnit import ConfigUnit
from ConfigURI import ConfigURI

from ConfigDPI import ConfigDPI
from ConfigKeyBinding import ConfigKeyBinding

from utils.HIGDialog import HIGDialog

import gtk
import gobject



class ConfigDialog(HIGDialog):
    """
      Class for the configuration dialog. This class handles the visualization
      of the dialog and loading / saving the configuration.
    """

    # mapping between item types and their widgets
    __ITEM_TABLE = {"boolean": ConfigBoolean,
                    "button": ConfigButton,
                    "color": ConfigColor,
                    "enum": ConfigEnum,
                    "float": ConfigFloat,
                    "font": ConfigFont,
                    "integer": ConfigInteger,
                    "string": ConfigString,
                    "title": ConfigTitle,
                    "unit": ConfigUnit,
                    "uri": ConfigURI,
                    
                    "dpi": ConfigDPI,
                    "keybinding": ConfigKeyBinding
                    }


    def __init__(self):

        # the instantiated items
        self.__children = []

        # getter, setter, and caller for getting and settings values and
        # calling callbacks
        self.__getter = None
        self.__setter = None
        self.__caller = None

        self.__close_callback = None

        # a banner
        self.__banner = None


        HIGDialog.__init__(self, buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE),
                           self_destroy = False)

        self.__tooltips = gtk.Tooltips()
        self.__tooltips.enable()


        def destroy(*args):
            if (self.__close_callback): self.__close_callback()
            
            self.hide()
            return True  # return True so that the window doesn't get destroyed

        self.connect("response", destroy)
        self.connect("delete-event", destroy)  # catch the close button as well


    def _set_setter(self, setter): self.__setter = setter
    def _set_getter(self, getter): self.__getter = getter
    def _set_caller(self, caller): self.__caller = caller

    def set_close_callback(self, handler): self.__close_callback = handler


    def _set_value(self, key, value, datatype):

        self.__setter(key, value, datatype)


    def _get_value(self, key):

        return self.__getter(key)


    def _invoke_callback(self, name, *args):

        try:
            self.__caller(name, *args)
        except KeyError:
            raise UserError(_("Invalid Function Call"),
                           _("There is no function called <b>%s</b>.\nThis "
                             "means that there's an error in the desklet's "
                             "code. You should inform the author of the "
                             "desklet about this problem." % (name,)))

        except StandardError, exc:
            log("An unknown error occured: %s" % (exc,))



    #
    # Creates a banner. This method has to be called before building the dialog
    # if a banner is desired.
    #
    def set_banner(self, icon, text):

        self.__banner = gtk.Frame()
        self.__banner.set_shadow_type(gtk.SHADOW_IN)
        self.__banner.show()

        b_box = gtk.HBox(spacing = 12)
        b_box.set_border_width(6)
        b_box.show()
        self.__banner.add(b_box)

        if (icon):
            try:
                # for him who loves small try blocks: you don't gain anything
                # from splitting up this block except for badly readable code ;)
                from utils import vfs
                data = vfs.read_entire_file(icon)
                loader = gtk.gdk.PixbufLoader()
                loader.write(data, len(data))
                loader.close()
                pbuf = loader.get_pixbuf()

                # scale icon down while preserving aspect ratio
                width = pbuf.get_width()
                height = pbuf.get_height()
                scale = 48 / float(height)
                width *= scale
                if (abs(scale - 1.0) > 0.001):
                    pbuf = pbuf.scale_simple(int(width), 48, 3)

                b_icon = gtk.Image()
                b_icon.set_from_pixbuf(pbuf)
                b_icon.show()
                b_box.pack_start(b_icon, False, False)

            except:
                pass

        #end if

        b_label = gtk.Label(text)
        b_label.set_use_markup(True)
        b_label.show()
        b_box.pack_start(b_label, True, True)



    #
    # Creates a configuration item of the given type.
    #
    def __create_config_item(self, itype, settings):

        try:
            itemclass = self.__ITEM_TABLE[itype]
        except KeyError:
            log("No such preferences item: %s" % (itype,))
            return None

        item = itemclass(itype, self._get_value, self._set_value,
                         self._invoke_callback)

        return item



    #
    # Adds a line of configuration widgets to the given page.
    #
    def __add_line(self, page, page_lines, indent, widgets, help):

        ebox = gtk.EventBox()
        ebox.show()

        if (len(widgets) == 2):
            page.attach(widgets[0], 0, 1, page_lines - 1, page_lines,
                        gtk.FILL, 0, indent, 3)
            ebox.add(widgets[1])
            page.attach(ebox, 1, 2, page_lines - 1, page_lines,
                        gtk.EXPAND | gtk.FILL, 0, 0, 3)

        else:
            ebox.add(widgets[0])
            page.attach(ebox, 0, 2, page_lines - 1, page_lines,
                        gtk.EXPAND | gtk.FILL, 0, indent, 3)

        if (help):
            self.__tooltips.set_tip(ebox, help)



    #
    # Builds up the dialog. This must be done before loading the configuration.
    #
    def build(self, items):

        if (self.__banner):
            self.vbox.pack_start(self.__banner, False, False)

        if (not items):
            label = gtk.Label(_("This desklet is not configurable."))
            label.show()
            self.vbox.pack_start(label, False, False)

        page_lines = 0
        page = gtk.Table(1, 2)
        page.show()
        notebook = None
        item_list = []
        self.__children = []

        for itype, settings in items:
            if (itype == "page"):
                if (not notebook):
                    align = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
                    align.show()
                    notebook = gtk.Notebook()
                    notebook.set_property("border-width", 6)
                    notebook.show()
                    align.add(notebook)
                    self.vbox.pack_start(align, False, False, 0)

                label = settings.get("label", "")
                tab = gtk.Label(label)
                tab.show()
                box = gtk.VBox()
                box.set_property("border-width", 12)
                box.show()
                box.add(page)
                notebook.append_page(box, tab)

                # create a new page
                page_lines = 0
                page = gtk.Table(1, 2)
                page.show()

            elif (itype == "item"):
                label = settings.get("label", "")
                value = settings.get("value", "")
                item_list.append((label, value))

            else:
                configitem = self.__create_config_item(itype, settings)
                if (not configitem): continue

                widgets = configitem.get_widgets()
                if (itype not in ("title", "button")):
                    configitem.set_prop_from_string("bind", settings["bind"])
                if (itype == "enum"): configitem.set_prop("items", item_list)
                for k, v in settings.items():
                    configitem.set_prop_from_string(k, v)

                help = settings.get("help", "")

                indent = (itype != "title") and 12 or 0
                page_lines += 1
                page.resize(page_lines, 2)
                if (itype == "title" and page_lines != 1):
                    # keep some HIGgy space above the title, but not if it's
                    # the first line
                    w, h = widgets[0].size_request()
                    widgets[0].set_size_request(-1, h + 12)
                self.__add_line(page, page_lines, indent, widgets, help)
                if (itype != "title"):
                    self.__children.append(configitem)

                item_list = []

            #end if

        #end for

        # add the only page manually if there's no notebook
        if (not notebook):
            self.vbox.pack_start(page, False, False, 0)


    #
    # Returns a list of the config items.
    #
    def get_config_items(self):

        return self.__children


    #
    # Sets the current working directory.
    #
    def set_path(self, path):

        for c in self.get_config_items(): c.set_path(path)


    #
    # Refine the show() method to update the configuration widgets.
    #
    def show(self):

        # have the children update themselves
        for c in self.get_config_items(): c.update()

        self.present()

        # run the updater
        gobject.timeout_add(500, self.__updater)



    def __updater(self):

        for c in self.get_config_items(): c.update()

        # stop the timer if the dialog is no longer visible
        if (self.get_property("visible")):
            return True
        else:
            return False

