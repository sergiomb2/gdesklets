from ConfigWidget import ConfigWidget
from utils.datatypes import *
from utils import vfs

import gtk
import os

class ConfigURI(ConfigWidget):

    def __init__(self, name, getter, setter, caller):

        self.__action_value = gtk.FILE_CHOOSER_ACTION_OPEN

        ConfigWidget.__init__(self, name, getter, setter, caller)

        self._register_property("value", TYPE_STRING, self._setp_value,
                                self._getp, "", doc = "Value")

        self._register_property("action", TYPE_STRING, self._setp_action,
                                self._getp, "", doc = "The file selection action")



    def get_widgets(self):

        def open_filedialog(src, self, entry):
            def response_cb(src, response):
                if (response == gtk.RESPONSE_OK):
                    fname = src.get_filename()
                    if (fname):
                        entry.set_text(fname)
                        self.__on_change(entry, None)
                    src.destroy()
                else:
                    src.destroy()

            def preview_cb(src):
                fname = src.get_preview_filename()
                success = src.get_preview_widget().preview(fname)
                self.__dialog.set_preview_widget_active(success)


            preview = _FileChooserPreview()
            preview.show()
            self.__dialog = gtk.FileChooserDialog("", None,
                                      gtk.FILE_CHOOSER_ACTION_OPEN,
                                      (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            self.__dialog.set_action(self.__action_value)
            self.__dialog.set_local_only(False)
            path = os.path.join(self._get_path(), entry.get_text())
            self.__dialog.set_current_folder_uri(os.path.dirname(path))
            self.__dialog.set_filename(os.path.abspath(path))
            self.__dialog.set_preview_widget(preview)
            self.__dialog.set_preview_widget_active(False)
            self.__dialog.set_use_preview_label(False)
            self.__dialog.show()
            self.__dialog.connect("response", response_cb)
            self.__dialog.connect("selection-changed", preview_cb)


        self.__label = gtk.Label("")
        self.__label.show()
        align = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        align.show()
        align.add(self.__label)

        hbox = gtk.HBox()
        hbox.show()
        self.__entry = gtk.Entry()
        self.__entry.show()
        hbox.pack_start(self.__entry, True, True, 0)

        btn = gtk.Button(stock = gtk.STOCK_OPEN)
        btn.show()
        hbox.pack_end(btn, True, True, 4)

        btn.connect("clicked", open_filedialog, self, self.__entry)
        self.__entry.connect("focus-out-event", self.__on_change)

        # we need an EventBox for being able to display tooltips
        self.__ebox = gtk.EventBox()
        self.__ebox.show()
        self.__ebox.add(hbox)

        return (align, self.__ebox)


    def __on_change(self, src, event):

        value = src.get_text()
        self._set_config(value)


    def _set_label(self, value): self.__label.set_text(value)
    def _set_enabled(self, value): self.__ebox.set_sensitive(value)


    def _setp_action(self, key, value):

        if (value == "save"): self.__action_value = gtk.FILE_CHOOSER_ACTION_SAVE 
        elif (value == "select_folder"): self.__action_value = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER 
        elif (value == "create_folder"): self.__action_value = gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER 
        else: self.__action_value = gtk.FILE_CHOOSER_ACTION_OPEN 

        self._setp(key, value)


    def _setp_value(self, key, value):

        self.__entry.set_text(value)
        self._set_config(value)
        self._setp(key, value)



#
# Preview widget for previewing files. Returns whether the given file could be
# displayed.
#
class _FileChooserPreview(gtk.Frame):

    def __init__(self):

        gtk.Frame.__init__(self)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.__img = gtk.Image()
        self.__img.show()
        self.add(self.__img)


    def preview(self, filename):

        loader = gtk.gdk.PixbufLoader()
        try:
            fd = vfs.open(filename)
            data = fd.read(3 * 1024 * 1024)  # read a maximum of 3 MB
            fd.close()
            loader.write(data, len(data))

        except:
            try:
                loader.close()
            except:
                pass
            return False

        try:
            loader.close()
        except:
            return False

        pbuf = loader.get_pixbuf()
        if (pbuf == None):
            return False

        # scale image down while preserving aspect ratio
        width = pbuf.get_width()
        height = pbuf.get_height()
        if (width > 180):
            scale = 180 / float(width)
            height *= scale
            height = max(1, height)
            if (abs(scale - 1.0) > 0.001):
                pbuf = pbuf.scale_simple(180, int(height), 3)

        self.__img.set_size_request(180, -1)
        self.__img.set_from_pixbuf(pbuf)
        self.__img.set_size_request(180, -1)
        del pbuf
        import gc; gc.collect()

        return True
