from libdesklets.controls import Control
from IPopUp import IPopUp

import gtk
from main import HOME
import os.path


class PopUp(Control, IPopUp):
  ''' 
      @author  Bjoern Koch <H.Humpel[AT]gmx.de>
      @version 0.1_alpha (25.07.2010)
  '''

  def __init__(self):
    self._text = ""
    self._icon = ""
    self._icon_position = "left"
    self._buttons = []

    self._visible = False

    self._event = ""
    self._error = ""
    self._status = "OK"

    # taken from utils/HIGDialog.py
    self._dialog = gtk.Dialog("gDesklets - IPopUp",
                              None,
                              gtk.DIALOG_DESTROY_WITH_PARENT | gtk.WINDOW_TOPLEVEL,
                              None)

    # handle any events closing the requester without using any of the buttons
    self._dialog.connect("close",  self.requester_closed)
    self._dialog.connect("delete_event",  self.requester_closed)
    self._dialog.connect("destroy",  self.requester_closed)

    # HIG says don't show a separator
    self._dialog.set_property("has-separator", False)
    # HIG says don't show up in the taskbar
    self._dialog.set_property("skip-taskbar-hint", True)
    # HIG says dialog mustn't be resizable
    self._dialog.set_property("resizable", False)
    # HIG says border-width must be set to 6
    self._dialog.set_property("border-width", 6)

    self._dialog.vbox.set_property("spacing", 12)

    # hbox1: the top horizontal box
    hbox1 = gtk.HBox()
    hbox1.set_property("spacing", 12)
    hbox1.set_property("border-width", 6)
    hbox1.show()

    # hbox2: the bottom horizontal box (only used if the icon is above the text)
    hbox2 = gtk.HBox()
    hbox2.set_property("spacing", 12)
    hbox2.set_property("border-width", 6)
    hbox2.show()

    # the icon box 
    self._icon_box = gtk.Image()
    self._icon_box.set_property("yalign", 0.0)
    self._icon_box.set_from_stock(self._icon, gtk.ICON_SIZE_DIALOG)
    self._icon_box.hide()
    # this one goes into the top-left corner
    hbox1.pack_start(self._icon_box, False, False, 0)

    self._dialog.vbox.pack_start(hbox1, False, False, 0)
    self._dialog.vbox.pack_start(hbox2, False, False, 0)

    # label1 will be the top-right corner (in hbox1), displayed if the icon-position is "left"
    self._label1 = gtk.Label()
    self._label1.set_property("use-markup", True)
    self._label1.set_property("selectable", True)
    self._label1.set_property("wrap", True)
    self._label1.set_property("yalign", 0.0)
    self._label1.set_label(self._text)
    self._label1.show()
    hbox1.pack_start(self._label1, False, False, 0)

    # label2 will be the bottom (in hbox2), displayed if the icon-position is "top"
    self._label2 = gtk.Label()
    self._label2.set_property("use-markup", True)
    self._label2.set_property("selectable", True)
    self._label2.set_property("wrap", True)
    self._label2.set_property("yalign", 0.0)
    self._label2.set_label(self._text)
    self._label2.hide()
    hbox2.pack_start(self._label2, False, False, 0)

    # check if the hboxes are already added to the vbox
    if (not isinstance(self._dialog.vbox.get_children()[0], gtk.HBox)):
       self._dialog.vbox.pack_start(hbox1, False, False, 0)
       self._dialog.vbox.pack_start(hbox2, False, False, 0)

    # some basic decorations
    path2icon = os.path.join(HOME, "data/gdesklets.png")
    self._dialog.set_icon_from_file(path2icon)

    # call constructor of super class
    Control.__init__(self)


### additional functions
  def destroy_all_buttons(self):
    for button in self._buttons:
      button.destroy()
    self._buttons = []
    self._event = ""


  def button_clicked(self, widget, event):
    self.__set_visible(False)
    self._event = event
    self._update("event")
    return True


  def requester_closed(self, widget, event):
    self.__set_visible(False)
    self._event = None
    self._update("event")
    return True


### getters and setters
  def __set_text(self, value):
    self._text = value
    self._label1.set_label(self._text)
    self._label2.set_label(self._text)


  def __set_icon(self, icon):
    # FIXME! this seems to be bad, but at least it is working (somehow)
    # check if an icon and a positon is given (len == 2)
    if (len(icon) == 2):
      self._icon = icon[0]
      self._icon_position = icon[1]
    else:
      self._icon = icon
      self._icon_position = 'left'

    stock_id = gtk.stock_lookup(self._icon)

    if (stock_id):
      self._icon_box.set_from_stock(self._icon, gtk.ICON_SIZE_DIALOG)
      self._icon_box.show()
    else:
      print "Warning from IPopUp:\n Unknown stock-icon for the main icon: '"+str(self._icon)+"'."
      self._icon_box.hide()

    if (self._icon_position == 'top'):
      self._label1.hide()
      self._label2.show()
    else:
      if (self._icon_position != 'left'):
        print "Warning from IPopUp:\n Unknown position for the main icon: '"+str(self._icon_position)+"'. Using 'left' as default."
        self._icon_position = 'left'
      self._label1.show()
      self._label2.hide()

  def __set_buttons(self, value):
    if (self._visible == False):
      self.destroy_all_buttons()
      i = 0
      for button in value:
        current_button = self._dialog.add_button(button[1], i)
        current_button.connect("clicked", self.button_clicked, button[0])
        current_button.set_use_stock(True)

        stock_id = gtk.stock_lookup(button[1])

        # do we have an icon (len == 3) and/but no stock icon: use the given one
        # or: if we have a stock-icon: use it and ignore the other icon given
        if ((len(button) == 3) and (not stock_id)):
          stock_id = gtk.stock_lookup(button[2])
        # if there is any icon: show it
        if (stock_id):
          current_button_icon = gtk.Image()
          current_button_icon.set_from_stock(stock_id[0], gtk.ICON_SIZE_BUTTON)
          current_button.set_image(current_button_icon)
          current_button_icon.show()

        self._buttons.append(current_button)
        i += 1
    else:
      print "Warning from IPopUp:\n The requester is still/already visible, so you cannot change or add any buttons!"


  def __set_visible(self, value):
    if (value):
      self._dialog.show()
    else:
      self._dialog.hide_on_delete()
    self._visible = value


  def __get_visible(self):
    return (self._visible)



  def __get_event(self):
    return (self._event)

  def __get_error(self):
    return (self._error)

  def __get_status(self):
    return (self._status)


###   Properties definitions
  text = property(fset=__set_text, doc = "The main text of the requester, supports pango markup.")
  icon = property(fset=__set_icon, doc = "The main icon of the requester and its position (stock-icon [,('left'|'top')]). Default position is 'left'.")
  buttons = property(fset=__set_buttons, doc = "A list of buttons [ [value1, text1[, stock-icon1]] [, [value2, text2[, stock-icon2]], ...] ]. If 'text' is the same as 'stock-icon' the default stock-text for this stock-icon will be displayed.")

  visible = property(fget=__get_visible, fset=__set_visible, doc = "Visibility state of the requester. Either true (visible) or false (hidden).")

  event = property(fget=__get_event, doc = "Get the return event of the requester (value of the button pushed or 'None' if the requester has been destroyed). Bindable.")
  error = property(fget=__get_error, doc = "Error information.")
  status = property (fget=__get_status, doc = "Status of the Control. Bindable.")


def get_class(): return PopUp

