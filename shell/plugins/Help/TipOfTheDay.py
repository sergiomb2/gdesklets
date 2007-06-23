from utils.Observable import Observable

from tips import TIPS

import gtk


#
# Class for tip-of-the-day dialogs.
#
class TipOfTheDay(gtk.MessageDialog, Observable):

    OBS_TIP = 0
    OBS_TOGGLED = 1


    def __init__(self, index):

        self.__index = index - 1

        gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_NONE,
                                   "gDesklets")
        self.set_title(_("Tip of the Day"))

        self.__label = self.vbox.get_children()[0].get_children()[1]
        # HACK HACK HACK -- make it work with gtk+-2.6.x
        if (not isinstance(self.__label, gtk.Label)):
            self.__label.remove(self.__label.get_children()[1])
            self.__label = self.__label.get_children()[0]

        self.__checkbox = gtk.CheckButton(_("Show tips at startup"))
        self.__checkbox.set_active(True)
        self.__checkbox.connect("toggled", self.__on_toggle)
        self.__checkbox.show()
        self.vbox.pack_end(self.__checkbox, 0, 0, 0)

        btn_prev = gtk.Button(stock = gtk.STOCK_GO_BACK)
        btn_prev.connect("clicked", self.prev_tip)
        btn_prev.show()

        btn_next = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        btn_next.connect("clicked", self.next_tip)
        btn_next.show()

        btn_close = gtk.Button(stock = gtk.STOCK_CLOSE)
        btn_close.connect("clicked", self.__on_close)
        btn_close.show()

        self.action_area.add(btn_prev)
        self.action_area.add(btn_next)
        self.action_area.add(btn_close)

        # make the close button the default button
        btn_close.set_flags(gtk.CAN_DEFAULT)
        self.set_default(btn_close)
        self.set_focus(btn_close)


    def set_show(self, value):

        self.__checkbox.set_active(value)


    def __on_close(self, src):

        self.hide()


    def __on_toggle(self, src):

        value = src.get_active()
        self.update_observer(self.OBS_TOGGLED, value)


    def next_tip(self, *args):

        self.__index += 1
        if (self.__index >= len(TIPS)): self.__index = 0

        self.__label.set_markup(_(TIPS[self.__index]).strip())
        self.update_observer(self.OBS_TIP, self.__index + 1)


    def prev_tip(self, *args):

        self.__index -= 1
        if (self.__index < 0): self.__index = len(TIPS) + self.__index

        self.__label.set_markup(_(TIPS[self.__index]).strip())
