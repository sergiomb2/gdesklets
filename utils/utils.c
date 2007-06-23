#include "utils.h"

#include <pygobject.h>
#include <gtk/gtk.h>


PyTypeObject * gdesklets_get_pygobject_type(void)
{
  static PyTypeObject *PyGObject_Type = NULL;

  if(G_UNLIKELY(PyGObject_Type == NULL))
    {
      PyObject *module;

      module = PyImport_ImportModule("gobject");

      if(!module)
        goto err_gobject;

      PyObject *moddict = PyModule_GetDict(module);

      PyGObject_Type = (PyTypeObject *) PyDict_GetItemString(moddict, "GObject");

      if (PyGObject_Type == NULL)
        goto err_gobject;
    }

  return PyGObject_Type;

 err_gobject:
  PyErr_SetString(PyExc_ImportError, "cannot import name GObject from gobject");
  return NULL;
}



int parse_gdk_window(PyObject *object, gpointer address)
{
  GdkWindow **window = address;

  if(!pygobject_check(object, gdesklets_get_pygobject_type()))
    goto err;

  if(!GDK_IS_WINDOW(pygobject_get(object)))
    goto err;

  *window = GDK_WINDOW(pygobject_get(object));

  return 1;

 err:
  PyErr_SetString(PyExc_TypeError, "first parameter must be a GdkWindow");
  return 0;
}


int parse_gdk_pixmap(PyObject *object, gpointer address)
{
  GdkPixmap **pmap = address;

  if(!pygobject_check(object, gdesklets_get_pygobject_type()))
    goto err;

  if(!GDK_IS_PIXMAP(pygobject_get(object)))
    goto err;

  *pmap = GDK_PIXMAP(pygobject_get(object));

  return 1;

 err:
  PyErr_SetString(PyExc_TypeError, "first parameter must be a GdkPixmap");
  return 0;
}


int parse_gdk_pixbuf(PyObject *object, gpointer address)
{
  GdkPixbuf **pixbuf = address;

  if(!pygobject_check(object, gdesklets_get_pygobject_type()))
    goto err;

  if(!GDK_IS_PIXBUF(pygobject_get(object)))
    goto err;

  *pixbuf = GDK_PIXBUF(pygobject_get(object));

  return 1;

 err:
  PyErr_SetString(PyExc_TypeError, "first parameter must be a GdkPixbuf");
  return 0;
}



int parse_gtk_image(PyObject *object, gpointer address)
{
  GtkImage **image = address;

  if(!pygobject_check(object, gdesklets_get_pygobject_type()))
    goto err;

  if(!GTK_IS_IMAGE(pygobject_get(object)))
    goto err;

  *image = GTK_IMAGE(pygobject_get(object));

  return 1;

 err:
  PyErr_SetString(PyExc_TypeError, "first parameter must be a GtkImage");
  return 0;
}



int parse_gtk_widget(PyObject *object, gpointer address)
{
  GtkWidget **widget = address;

  if(!pygobject_check(object, gdesklets_get_pygobject_type()))
    goto err;

  if(!GTK_IS_WIDGET(pygobject_get(object)))
    goto err;

  *widget = GTK_WIDGET(pygobject_get(object));

  return 1;

 err:
  PyErr_SetString(PyExc_TypeError, "first parameter must be a GtkWidget");
  return 0;
}
