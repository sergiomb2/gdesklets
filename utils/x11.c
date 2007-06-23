/* Functions for X11-related stuff.
 * Copyright (C) 2003 - 2005 Martin Grimme
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
 * 02111-1307, USA.
 */

#include "utils.h"

#include <gdk/gdk.h>
#include <gdk/gdkx.h>

#include <X11/Xatom.h>
#include <X11/Xlib.h>


#define _NET_WM_STATE_REMOVE        0    /* remove/unset property */
#define _NET_WM_STATE_ADD           1    /* add/set property */

#define ATOM(name) gdk_x11_get_xatom_by_name(name)

/* Declare entry point for python */
PyMODINIT_FUNC initx11(void);

/* boolean for indicating whether the event filter for keybindings has been
   set up */
static gboolean have_event_filter = FALSE;

static void
_change_state (GdkNativeWindow window, gboolean add, const gchar* atom,
               const gchar* state1, const gchar* state2)
{
  XEvent xev;

  xev.type                  = ClientMessage;
  xev.xclient.data.l[0]     = add ? _NET_WM_STATE_ADD : _NET_WM_STATE_REMOVE;
  xev.xclient.data.l[1]     = ATOM (state1);
  xev.xclient.data.l[2]     = state2 ? (glong) state2 : 0;
  xev.xclient.format        = 32;
  xev.xclient.message_type  = ATOM (atom);
  xev.xclient.type          = ClientMessage;
  xev.xclient.window        = window;

  XSendEvent(GDK_DISPLAY (), GDK_ROOT_WINDOW (), False, SubstructureNotifyMask,
             &xev);
}



static PyObject* set_above (PyObject *self, PyObject *args)
{
  gint32 value;
  GdkWindow *window;

  if (!PyArg_ParseTuple(args, "O&i", parse_gdk_window, &window, &value))
    return NULL;

  _change_state (GDK_WINDOW_XID(window), (gboolean) value, "_NET_WM_STATE",
                 "_NET_WM_STATE_ABOVE", NULL);

  Py_INCREF (Py_None);
  return Py_None;
}



static PyObject* set_below (PyObject *self, PyObject *args)
{
  gint32 value;
  GdkWindow *window;

  if (!PyArg_ParseTuple(args, "O&i", parse_gdk_window, &window, &value))
    return NULL;

  _change_state (GDK_WINDOW_XID(window), (gboolean) value, "_NET_WM_STATE",
                 "_NET_WM_STATE_BELOW", NULL);

  Py_INCREF (Py_None);
  return Py_None;
}



static PyObject* set_type_dock (PyObject *self, PyObject *args)
{
  gint32 value;
  GdkWindow *window;

  if (!PyArg_ParseTuple (args, "O&i", parse_gdk_window, &window, &value))
    return NULL;

  if (value)
    gdk_window_set_type_hint (window, GDK_WINDOW_TYPE_HINT_DOCK);
  else
    gdk_window_set_type_hint (window, GDK_WINDOW_TYPE_HINT_NORMAL);

  Py_INCREF (Py_None);
  return Py_None;
}



/* The purpose of this event filter is to intercept XEvents before they get
 * processed (and thrown away) by GDK, and turn them into GDK events for a
 * proxy window.
 */
static GdkFilterReturn
event_filter (GdkXEvent *gdk_xevent, GdkEvent *event, gpointer data) {

  GdkEventKey *keyevent;
  GdkWindow *proxy = (GdkWindow *) data;
  XEvent *xevent   = (XEvent *) gdk_xevent;
  KeyCode keycode  = xevent->xkey.keycode;
  guint modifiers  = xevent->xkey.state;

  /* we're only interested in KeyPress events */
  if (xevent->type == KeyPress) {

    event->type = GDK_KEY_PRESS;
    keyevent = (GdkEventKey *) event;
    /* mapping between X and GDK modifier keys is trivial! :) */
    keyevent->hardware_keycode  = keycode;
    keyevent->keyval            = 0;
    keyevent->length            = 0;
    keyevent->send_event        = FALSE;
    keyevent->state             = (GdkModifierType) modifiers;
    keyevent->string            = NULL;
    keyevent->time              = GDK_CURRENT_TIME;
    keyevent->window            = proxy;

    return GDK_FILTER_TRANSLATE;

  } else {

    return GDK_FILTER_CONTINUE;

  }

}



static PyObject *
grab_ungrab_key (PyObject *self, PyObject *args) {

  guint x_modifiers;
  gboolean is_grab;
  int keycode_int;
  KeyCode keycode;
  GdkModifierType modifiers;
  GdkWindow *window, *rootwindow;

  if (!PyArg_ParseTuple (args, "O&iii",
                         parse_gdk_window, &window,
                         &keycode_int, &modifiers, &is_grab))
    return NULL;

  keycode = (KeyCode) keycode_int;

  rootwindow = gdk_get_default_root_window ();

  /* set up event filter, if necessary */
  if (!have_event_filter) {

    gdk_window_add_filter (rootwindow,
                           (GdkFilterFunc) event_filter,
                           (gpointer) window);
    have_event_filter = TRUE;

  }

  /* map GDK modifiers to X modifiers; luckily they're currently the same,
     so there's not much to do */
  x_modifiers = (guint) modifiers;

  gdk_error_trap_push ();
  if (is_grab) {

    XGrabKey (GDK_WINDOW_XDISPLAY (rootwindow), keycode, x_modifiers,
              GDK_WINDOW_XWINDOW (rootwindow), False,
              GrabModeAsync, GrabModeAsync);

  } else {

    XUngrabKey (GDK_WINDOW_XDISPLAY (rootwindow), keycode, x_modifiers,
                GDK_WINDOW_XWINDOW (rootwindow));

  }
  /* wait until all requests have been processed by the server */
  gdk_flush ();
  /* check for errors */
  if (gdk_error_trap_pop ()) {
    PyErr_SetString (PyExc_RuntimeError, "XGrabKey()/XUngrabKey() failed!");
    return NULL;
  }

  Py_INCREF (Py_None);
  return Py_None;

}



PyMODINIT_FUNC
initx11(void)
{
  static const PyMethodDef methods[] =
    {
      {"set_above", set_above, METH_VARARGS, NULL},
      {"set_below", set_below, METH_VARARGS, NULL},
      {"set_type_dock", set_type_dock, METH_VARARGS, NULL},
      {"grab_ungrab_key", grab_ungrab_key, METH_VARARGS, NULL},
      {NULL, NULL, 0, NULL}
    };

  if (!gdesklets_get_pygobject_type())
    return;

  Py_InitModule ("x11", (PyMethodDef *) methods);
}
