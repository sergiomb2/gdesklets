/* Functions for using the systray.
 * Copyright (C) 2004 Martin Grimme
 * Copyright (C) 2004 Christian Meyer
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

#include "eggtrayicon.h"
#include "utils.h"


PyMODINIT_FUNC initsystray(void);

typedef struct _Icon Icon;

struct _Icon
{
  PyObject_HEAD
  /* Type-specific fields go here. */
  EggTrayIcon *icon;
};



static int icon_init(PyObject *self, PyObject *args, PyObject *kw)
{
  static const gchar * const kwnames[] = {"name", NULL};

  const gchar *name;
  Icon * const that = (Icon*) self;

  if(!PyArg_ParseTupleAndKeywords(args, kw, "s", (gchar **) kwnames, &name))
    return -1;

  that->icon = egg_tray_icon_new(name);
  gtk_widget_show (GTK_WIDGET (that->icon));

  return 0;
}



static void icon_dealloc(PyObject *self)
{
  Icon * const that = (Icon*) self;

  g_object_unref (G_OBJECT (that->icon));

  self->ob_type->tp_free(self);
}



static PyObject* icon_add(PyObject *self, PyObject* args)
{
  GtkWidget *child;
  Icon * const that = (Icon*) self;

  if(!PyArg_ParseTuple(args, "O&", parse_gtk_widget, &child))
    return NULL;

  gtk_container_add (GTK_CONTAINER (that->icon), child);

  Py_INCREF(Py_None);
  return Py_None;
}



PyMODINIT_FUNC
initsystray(void)
{
  static const PyMethodDef methods[] =
    {
      {NULL, NULL, 0, NULL}
    };


  static const PyMethodDef Icon_methods[] =
    {
      {"add", icon_add, METH_VARARGS, NULL},
      {NULL, NULL, 0, NULL}
    };


  static const PyTypeObject IconType =
    {
      PyObject_HEAD_INIT(NULL)
      0,                        /*ob_size*/
      "systray.Icon",           /*tp_name*/
      sizeof(Icon),             /*tp_basicsize*/
      0,                        /*tp_itemsize*/
      icon_dealloc,             /*tp_dealloc*/
      0,                        /*tp_print*/
      0,                        /*tp_getattr*/
      0,                        /*tp_setattr*/
      0,                        /*tp_compare*/
      0,                        /*tp_repr*/
      0,                        /*tp_as_number*/
      0,                        /*tp_as_sequence*/
      0,                        /*tp_as_mapping*/
      0,                        /*tp_hash */
      0,                        /*tp_call*/
      0,                        /*tp_str*/
      0,                        /*tp_getattro*/
      0,                        /*tp_setattro*/
      0,                        /*tp_as_buffer*/
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
      "EggSysTrayIcon",         /* tp_doc */
      0,                        /* tp_traverse */
      0,                        /* tp_clear */
      0,                        /* tp_richcompare */
      0,                        /* tp_weaklistoffset */
      0,                        /* tp_iter */
      0,                        /* tp_iternext */
      (PyMethodDef*) Icon_methods,             /* tp_methods */
      0,                        /* tp_members */
      0,                        /* tp_getset */
      0,                        /* tp_base */
      0,                        /* tp_dict */
      0,                        /* tp_descr_get */
      0,                        /* tp_descr_set */
      0,                        /* tp_dictoffset */
      icon_init,                /* tp_init */
      PyType_GenericAlloc,      /* tp_alloc */
      PyType_GenericNew,        /* tp_new */
      _PyObject_Del,            /* tp_free */
    };

  PyObject* module;

  if(!gdesklets_get_pygobject_type())
    return;

  module = Py_InitModule("systray", (PyMethodDef*) methods);
  PyType_Ready((PyTypeObject*)&IconType);
  PyObject_SetAttrString(module, "Icon", (PyObject*) &IconType);
}

