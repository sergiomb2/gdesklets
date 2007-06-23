import Xlib
from Xlib import X, display, protocol

def _change_state(window, add, atom, state):

    disp  = Xlib.display.Display()
    rootw = disp.screen().root
    ctype = disp.intern_atom(atom)
    state = disp.intern_atom(state)
    add   = add and 1 or 0

    # this is quite simple: data needs to be either of size 8, 16 or 32 byte
    # 8 and 16 are too small, since we have a long and an integer, as a result
    # we need 32 byte and do some padding: int + long + 3 * int = 32
    data = [add, state] + [0] * 3
    ev = Xlib.protocol.event.ClientMessage(client_type = ctype,
                                           window = window,
                                           data = (32, data))
    mask = X.SubstructureNotifyMask
    rootw.send_event(ev, event_mask = mask)


def set_above(win, val):

    _change_state(win.xid, val, "_NET_WM_STATE", "_NET_WM_STATE_ABOVE")


def set_below(win, val):

    _change_state(win.xid, val, "_NET_WM_STATE", "_NET_WM_STATE_BELOW")
