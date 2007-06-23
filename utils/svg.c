/* Functions for rendering SVG onto a GtkImage.
 * Copyright (C) 2004 Martin Grimme
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

#include <gtk/gtk.h>
#include <librsvg/rsvg.h>

PyMODINIT_FUNC initsvg(void);

static PyObject* render(PyObject *self, PyObject *args)
{
  GtkImage *image;
  GdkPixbuf *pbuf;
  GError *error = NULL;
  PyObject *string;
  RsvgHandle *handle;

  char *buffer;
  int length;
  int width, height;

  if(!PyArg_ParseTuple(args, "O&IIS", parse_gtk_image,
                       &image, &width, &height, &string))
    return NULL;

  if(PyString_AsStringAndSize(string, &buffer, &length) == -1)
    return NULL;

  if (!(handle = rsvg_handle_new ())) {
    g_error("Couldn't create handle!");
    return NULL;
  }
  if (!rsvg_handle_write (handle, (const guchar *)buffer, length, &error)) {
    g_error("Error writing buffer to handle: %s\n", error->message);
  }
  if (!rsvg_handle_close (handle, &error)) {
    g_error("Error closing handle: %s\n", error->message);
  }
  if (!(pbuf = rsvg_handle_get_pixbuf (handle))) {
    g_error("Error creating pixbuf from handle.");
  }
  else {
    gtk_image_set_from_pixbuf (image, pbuf);
    g_object_unref (G_OBJECT (pbuf));
  }
  rsvg_handle_free (handle);

  Py_INCREF(Py_None);
  return Py_None;
}



PyMODINIT_FUNC
initsvg(void)
{
  static const PyMethodDef methods[] =
    {
      {"render", render, METH_VARARGS, NULL},
      {NULL, NULL, 0, NULL}
    };

  if(!gdesklets_get_pygobject_type())
    return;

  Py_InitModule("svg", (PyMethodDef*) methods);
}
