import gtk
import os

#
# Class for giving feedback while loading a display.
#

class LoadingFeedback(gtk.Window):

    def __init__(self):

        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_CENTER)

        frm = gtk.Frame()
        frm.set_shadow_type(gtk.SHADOW_OUT)
        frm.show()
        self.add(frm)

        box = gtk.HBox(spacing = 12)
        box.set_border_width(12)
        box.show()
        frm.add(box)

        self.__icon = gtk.Image()
        box.pack_start(self.__icon)

        self.__label = gtk.Label("")
        self.__label.show()
        box.pack_end(self.__label)



    def set_loading(self, path):

        from MetaData import MetaData
        try:
            meta = MetaData(path)
            preview = meta.get(meta.KEY_PREVIEW)
        except Exception:
            preview = ""

        dirname = os.path.dirname(path)
        icon = os.path.join(dirname, preview)

        self.__label.set_markup("<big><b>Loading:</b>\n%s</big>" % path)

        self.__icon.hide()
        if (preview):
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
                if (width > 96): width = 96

                if (abs(scale - 1.0) > 0.001):
                    pbuf = pbuf.scale_simple(int(width), 48, 3)

                self.__icon.set_from_pixbuf(pbuf)
                self.__icon.show()

            except Exception:
                pass

        #end if

        self.resize(10, 10)
        self.set_size_request(-1, -1)

