from main import CREDITS

import gobject
import gtk
import os


class AboutDialog(gtk.Window):

    """ Class for a fancy "About" dialog. """

    def __init__(self, path):

        self.__is_stopped = True
        self.__scroller_values = ()

        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        self.set_title(_("About gDesklets"))
        self.connect("button-press-event", self.__on_close)
        self.connect("key-press-event", self.__on_close)
        self.connect("delete-event", self.__on_close)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)

        fixed = gtk.Fixed()
        self.add(fixed)

        img = gtk.Image()
        img.set_from_file(os.path.join(path, "about.png"))
        fixed.put(img, 0, 0)

        width, height = img.size_request()

        scroller = gtk.Fixed()
        scroller.set_size_request(width, height - 32)
        fixed.put(scroller, 0, 32)

        text = ""
        for header, body in CREDITS:
            text += "<b>" + header + "</b>\n\n"
            text += "\n".join(body)
            text += "\n\n\n\n"
        text = "<big>" + text.strip() + "</big>"

        credits = gtk.Label(text)
        credits.set_use_markup(True)
        credits.set_justify(gtk.JUSTIFY_CENTER)

        lbl_width, lbl_height = credits.size_request()
        scroller.put(credits, (width - lbl_width) / 2, height)

        self.__scroller = scroller
        self.__credits = credits

        self.__scroller_values = (height - 32, -lbl_height,
                                  (width - lbl_width) / 2)


    def __scroll(self, ycoord):

        begin, end, xcoord = self.__scroller_values
        self.__scroller.move(self.__credits, xcoord, ycoord)
        ycoord -= 1

        if (ycoord < end):
            ycoord = begin

        if (not self.__is_stopped):
            gobject.timeout_add(50, self.__scroll, ycoord)

        return False


    def __on_close(self, *args):

        self.__is_stopped = True
        self.hide()

        return True


    def show(self):

        if (not self.__is_stopped):
            return

        self.show_all()

        self.__is_stopped = False
        begin, end, xcoord = self.__scroller_values
        gobject.timeout_add(0, self.__scroll, begin)

