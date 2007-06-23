import gtk
import gobject
import sys
import traceback

from cStringIO import StringIO
from HIGDialog import HIGDialog
from LogView import LogView


# define some Dialog icons
_ERROR = gtk.STOCK_DIALOG_ERROR
_INFO = gtk.STOCK_DIALOG_INFO
_QUESTION = gtk.STOCK_DIALOG_QUESTION
_WARNING = gtk.STOCK_DIALOG_WARNING

# we only want to display one dialog at a time, so let's queue them
_dialog_queue = []

# IDs which are to skip
_skip_ids = []

# remember the previous message to avoid displaying the same message twice
# in a sequence
_last_message = None


#
# Adds a details button to the given dialog.
#
def _set_details(dialog, details):

    vbox1 = gtk.VBox()
    vbox2 = dialog.vbox
    vbox2.pack_start(vbox1)
    align1 = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
    align1.set_property("border-width", 6)
    align1.show()
    vbox2.pack_start(align1)

    align2 = gtk.Alignment(0.0, 0.0, 0.0, 0.0)
    align2.set_property("border-width", 6)
    align2.show()
    details = details.rstrip()
    expander = gtk.expander_new_with_mnemonic(
        _("_Details (%d lines)") % len(details.splitlines()))
    expander.show()
    viewport = gtk.ScrolledWindow()
    viewport.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
    viewport.show()
    lbl = LogView()
    lbl.append(details)
    lbl.show()
    nil, height = lbl.get_size_request()
    width, nil = vbox2.get_size_request()
    viewport.set_size_request(width, min(height, 480))
    viewport.add_with_viewport(lbl)
    expander.add(viewport)
    align2.add(expander)

    vbox1.show()
    vbox1.pack_start(align2)


#
# Queues the given dialog for displaying.
#
def _queue_dialog(ident, dialog):

    def proceed(*args):
        if (not _dialog_queue): return
        _dialog_queue.pop(0)
        if (not _dialog_queue): return
        
        ident, dialog = _dialog_queue[0]

        if (not ident in _skip_ids):
            dialog.present()
        else:
            dialog.destroy()
            proceed()
            

    dialog.connect("destroy", proceed)

    # display the dialog immediately if there are no others in the queue
    _dialog_queue.append((ident, dialog))
    if (len(_dialog_queue) == 1):
        dialog.present()


#
# Removes all dialogs associated with the given ID from the queue.
#
def forget(ident_to_forget):

    q = []
    for ident, dialog in _dialog_queue:
        if (ident != ident_to_forget): q.append((ident, dialog))
    _dialog_queue[:] = q

    if (ident_to_forget in _skip_ids): _skip_ids.remove(ident_to_forget)


#
# Displays an error dialog. Errors are critical and the program terminates
# afterwards.
#
def error(primary, secondary):

    dialog = HIGDialog((gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE),
                       _ERROR, primary, secondary)
    gtk.threads_enter()
    dialog.run()
    gtk.threads_leave()
    sys.exit(1337)


#
# Displays an information dialog.
#
def info(primary, secondary):

    dialog = HIGDialog((gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE),
                       _INFO, primary, secondary)
    _queue_dialog(0, dialog)


#
# Displays a question dialog.
#
def question(icon, primary, secondary, *buttons):

    def responder(src, response):
        callback = buttons[response][1]
        if (callback): callback()

    response = 0
    btns = []
    for label, callback in buttons:
        btns.append(label)
        btns.append(response)
        response += 1

    dialog = HIGDialog(tuple(btns), _QUESTION, primary, secondary)
    dialog.connect("response", responder)
    dialog.show()


#
# Displays a warning dialog.
#
def warning(primary, secondary, details = "", force = False):

    global _last_message

    # don't show the same dialog twice in a sequence
    if (force): _last_message = ""
    if (_last_message == (primary, secondary, details)): return
    else: _last_message = (primary, secondary, details)

    dialog = HIGDialog((gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE),
                       _WARNING, primary, secondary)


    if (details):
        _set_details(dialog, details)

    _queue_dialog(0, dialog)


#
# Displays a user error dialog. This dialog is for hilighting invalid lines
# of code and is associated with a display instance.
#
def user_error(ident, primary, secondary, details = ""):

    if (ident in _skip_ids): return

    dialog = HIGDialog((gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE),
                       _WARNING, primary, secondary)


    if (details):
        _set_details(dialog, details)

    def f(src, ident):
        if (src.get_active() and not ident in _skip_ids):
            _skip_ids.append(ident)
        elif (not src.get_active() and ident in _skip_ids):
            _skip_ids.remove(ident)
        
    vbox = dialog.vbox
    chkbtn = gtk.CheckButton(_("_Ignore errors from this desklet"))
    chkbtn.connect("toggled", f, ident)
    chkbtn.show()
    vbox.pack_start(chkbtn)

    _queue_dialog(ident, dialog)

    


#
# Use the new filechoose if possible, or fallback to the old one
#
def fileselector(title, callback_ok, callback_cancel, *args):

    def handler(src, response):
        if (response == gtk.RESPONSE_OK):
            if (callback_ok): callback_ok(src, *args)
        else:
            if (callback_cancel): callback_cancel(src, *args)
            else: src.destroy()


    # do we have FileChooserDialog available?
    try:
        fsel = gtk.FileChooserDialog(title, None,
                                     gtk.FILE_CHOOSER_ACTION_OPEN,
                                     (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                      gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        fsel.connect("response", handler)

    # no, then use the old FileSelection
    except:
        def f(btn, fsel, response): handler(fsel, response)

        fsel = gtk.FileSelection()

        if (title): fsel.set_title(title)
        fsel.ok_button.connect("clicked", f, fsel, gtk.RESPONSE_OK)
        fsel.cancel_button.connect("clicked", f, fsel, gtk.RESPONSE_CANCEL)

    fsel.show()

