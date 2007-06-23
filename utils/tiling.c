#include "render.h"
#include "utils.h"

#include <pygtk/pygtk.h>


/* similar to PyObject_HEAD but for PyGObject */
#define PyGObject_HEAD PyObject_HEAD \
                       GObject *obj; \
                       PyObject *inst_dict; \
                       PyObject *weakreflist; \
                       GSList *closures;

/* type of base class */
static PyTypeObject *_PyGtkImage_Type;
#define PyGtkImage_Type (*_PyGtkImage_Type)

/* type of TImage */
typedef struct {
  PyGObject_HEAD
  guint width;
  guint height;
  gboolean invalidated;

  GdkPixbuf *pbuf;
} TImage;
#define TIMAGE(object) ((TImage *) object)

/* Declare entry point for python */
PyMODINIT_FUNC inittiling(void);


static int
tiling_init (PyObject *self, PyObject *args, PyObject *kwargs)
{
  if (!PyArg_ParseTuple(args, ""))
    return -1;

  TIMAGE (self)->obj = g_object_new (GTK_TYPE_IMAGE, NULL);

  if (!G_UNLIKELY (TIMAGE (self)->obj)) {
    PyErr_SetString (PyExc_RuntimeError, "Couldn't create TImage object");
    return -1;
  }

  pygobject_register_wrapper (self);

  TIMAGE (self)->invalidated = TRUE;
  TIMAGE (self)->width       = 1;
  TIMAGE (self)->height      = 1;
  TIMAGE (self)->pbuf        = NULL;

  return 0;
}


static void
tiling_dealloc (TImage *self)
{
  GdkPixbuf *pbuf;
  GObject *obj;

  obj = TIMAGE (self)->obj;
  pbuf = TIMAGE (self)->pbuf;

  if (G_UNLIKELY (obj != NULL)) {
    g_object_unref (obj);
    obj = NULL;
  }
  if (G_LIKELY (pbuf != NULL)) {
    g_object_unref (pbuf);
    pbuf = NULL;
  }

  self->ob_type->tp_free ((PyObject *) self);
}


static PyObject *
get_size (PyObject *self)
{
  guint width, height;

  width = gdk_pixbuf_get_width (TIMAGE (self)->pbuf);
  height = gdk_pixbuf_get_height (TIMAGE (self)->pbuf);

  return Py_BuildValue ("(ii)", width, height);
}



static PyObject *
set_from_color (PyObject *self, PyObject *args)
{
  guint r, g, b, a;
  guint32 color;

  if (!PyArg_ParseTuple (args, "iiii", &r, &g, &b, &a))
    return NULL;

  color = (r << 24) + (g << 16) + (b << 8) + a;

  /* kill old pixbuf */
  if (G_LIKELY (TIMAGE (self)->pbuf))
    g_object_unref (TIMAGE (self)->pbuf);

  /* make new pixbuf */
  TIMAGE (self)->pbuf = gdk_pixbuf_new (GDK_COLORSPACE_RGB, TRUE, 8, 320, 32);
  gdk_pixbuf_fill (TIMAGE (self)->pbuf, color);
  TIMAGE (self)->invalidated = TRUE;

  Py_INCREF (Py_None);
  return Py_None;
}


static PyObject *
set_from_data (PyObject *self, PyObject *args)
{
  guint length;
  guchar *data;

  GdkPixbufLoader *loader;
  GdkPixbuf *alphaified;
  GError *error = NULL;

  if (!PyArg_ParseTuple (args, "s#", &data, &length))
    return NULL;

  /* kill old pixbuf */
  if (G_LIKELY (TIMAGE (self)->pbuf))
    g_object_unref (TIMAGE (self)->pbuf);

  /* make new pixbuf */
  loader = g_object_new (GDK_TYPE_PIXBUF_LOADER, NULL);
  if (!gdk_pixbuf_loader_write (loader, data, length, &error)) {
    PyErr_SetString(PyExc_RuntimeError, "Invalid image format");
    g_error_free (error);
    return NULL;
  }
  if (!gdk_pixbuf_loader_close (loader, &error)) {
    PyErr_SetString(PyExc_RuntimeError, "Couldn't read image");
    g_error_free (error);
    return NULL;
  }

  TIMAGE (self)->pbuf = gdk_pixbuf_loader_get_pixbuf (loader);

  /* we require an alpha channel */
  alphaified = gdk_pixbuf_add_alpha (TIMAGE (self)->pbuf, FALSE, 0, 0, 0);
  g_object_unref (TIMAGE (self)->pbuf);
  TIMAGE (self)->pbuf = alphaified;

  TIMAGE (self)->invalidated = TRUE;

  Py_INCREF (Py_None);
  return Py_None;
}


static PyObject *
set_from_file (PyObject *self, PyObject *args)
{
  gchar *filename;
  GdkPixbuf *alphaified;
  GError *error = NULL;

  if (!PyArg_ParseTuple (args, "s", &filename))
    return NULL;

  /* kill old pixbuf */
  if (G_LIKELY (TIMAGE (self)->pbuf))
    g_object_unref (TIMAGE (self)->pbuf);

  /* make new pixbuf */
  if (!(TIMAGE (self)->pbuf = gdk_pixbuf_new_from_file (filename, &error))) {
    PyErr_SetString(PyExc_RuntimeError, "Invalid image format");
    g_error_free (error);
    return NULL;
  }

  /* we require an alpha channel */
  alphaified = gdk_pixbuf_add_alpha (TIMAGE (self)->pbuf, FALSE, 0, 0, 0);
  g_object_unref (TIMAGE (self)->pbuf);
  TIMAGE (self)->pbuf = alphaified;

  TIMAGE (self)->invalidated = TRUE;

  Py_INCREF (Py_None);
  return Py_None;
}



static PyObject *
set_from_drawable (PyObject *self, PyObject *args)
{
  guint alpha;
  guint i, offset;
  gint rowstride, width, height;
  guchar *data;
  gboolean restore_alpha = FALSE;
  GdkPixmap *pmap;
  GdkPixbuf *alphaified;


  if (!PyArg_ParseTuple (args, "O&|h", parse_gdk_pixmap, &pmap, &restore_alpha))
    return NULL;

  /* kill old pixbuf */
  if (G_LIKELY (TIMAGE (self)->pbuf))
    g_object_unref (TIMAGE (self)->pbuf);

  /* make new pixbuf */
  gdk_drawable_get_size (pmap, &width, &height);
  TIMAGE (self)->pbuf = gdk_pixbuf_get_from_drawable (NULL, pmap, NULL, 0, 0,
                                                      0, 0, width, height);

  /* we require an alpha channel */
  alphaified = gdk_pixbuf_add_alpha (TIMAGE (self)->pbuf, FALSE, 0, 0, 0);
  g_object_unref (TIMAGE (self)->pbuf);

  if (restore_alpha) {
    rowstride = gdk_pixbuf_get_rowstride (alphaified);
    data = gdk_pixbuf_get_pixels (alphaified);
    offset = (height >> 1) * rowstride;
    for (i = 0; i < offset; i+= 4) {

      /* restore alpha channel */
      alpha = 255 + data[i] - data[offset + i];
      data[i + 3] = alpha;

      /* restore original color */
      if (alpha > 0) {
        data[i] = MIN(255, data[i] / (alpha / 255.0));
        data[i + 1] = MIN(255, data[i + 1] / (alpha / 255.0));
        data[i + 2] = MIN(255, data[i + 2] / (alpha / 255.0));
      }
    }

    TIMAGE (self)->pbuf = gdk_pixbuf_new_subpixbuf (alphaified,
                                                    0, 0, width, height >> 1);
    g_object_unref (alphaified);

  } else {
    TIMAGE (self)->pbuf = alphaified;
  }

  TIMAGE (self)->invalidated = TRUE;

  Py_INCREF (Py_None);
  return Py_None;
}


static PyObject *
render (PyObject *self, PyObject *args)
{
  guint width, height;
  gfloat opacity, saturation;

  if (!PyArg_ParseTuple (args, "iiff", &width, &height, &opacity, &saturation))
    return NULL;

  render_to_image (GTK_IMAGE (TIMAGE (self)->obj), TIMAGE (self)->pbuf,
                   width, height, opacity, saturation);

  Py_INCREF (Py_None);
  return Py_None;

}

static PyObject *
tile (PyObject *self, PyObject *args)
{
  guint width, height;
  GdkPixbuf *background;

  if (!PyArg_ParseTuple (args, "ii", &width, &height))
    return NULL;

  if (width == 0 || height == 0) {
    Py_INCREF (Py_None);
    return Py_None;
  }

  if (TIMAGE (self)->pbuf && (TIMAGE (self)->invalidated ||
                              TIMAGE (self)->width != width ||
                              TIMAGE (self)->height != height))
  {
    TIMAGE (self)->invalidated = FALSE;
    TIMAGE (self)->width = width;
    TIMAGE (self)->height = height;

    background = gdk_pixbuf_new (GDK_COLORSPACE_RGB, TRUE, 8, width, height);
    render_tile (TIMAGE (self)->pbuf, background);

    gtk_image_set_from_pixbuf (GTK_IMAGE (TIMAGE (self)->obj), background);

    g_object_unref (background);
  }

  Py_INCREF (Py_None);
  return Py_None;
}


static PyObject *
set_from_background (PyObject *self, PyObject *args)
{
  guint x, y, width, height;
  glong wallpaper_id;

  if (!PyArg_ParseTuple (args, "liiii", &wallpaper_id, &x, &y, &width, &height))
    return NULL;

  if (width == 0 || height == 0) {
    Py_INCREF (Py_None);
    return Py_None;
  }

  /* kill old pixbuf */
  if (G_LIKELY (TIMAGE (self)->pbuf))
    g_object_unref (TIMAGE (self)->pbuf);

  /* make new pixbuf */
  TIMAGE (self)->pbuf = gdk_pixbuf_new (GDK_COLORSPACE_RGB, TRUE, 8,
                                        width, height);
  if (wallpaper_id)
    render_background (TIMAGE (self)->pbuf, wallpaper_id, x, y, width, height);
  else
    render_background_fallback (TIMAGE (self)->pbuf, x, y, width, height);
  TIMAGE (self)->invalidated = TRUE;

  Py_INCREF (Py_None);
  return Py_None;

}


static PyMethodDef tiling_functions[] = { {NULL} };


static PyMethodDef tiling_methods[] = {
  {"get_size", (PyCFunction) get_size, METH_NOARGS, NULL},
  {"set_from_color", (PyCFunction) set_from_color, METH_VARARGS, NULL},
  {"set_from_data", (PyCFunction) set_from_data, METH_VARARGS, NULL},
  {"set_from_file", (PyCFunction) set_from_file, METH_VARARGS, NULL},
  {"set_from_drawable", (PyCFunction) set_from_drawable, METH_VARARGS, NULL},
  {"set_from_background", (PyCFunction) set_from_background, METH_VARARGS, NULL},
  {"tile", (PyCFunction) tile, METH_VARARGS, NULL},
  {"render", (PyCFunction) render, METH_VARARGS, NULL},
  {NULL}
};


static PyTypeObject t_tiling = {
  PyObject_HEAD_INIT(NULL)
  0,                                           /*tp_internal*/
  "tiling.Tiling",                             /*tp_name*/
  sizeof(TImage),                              /*tp_basicsize*/
  0,                                           /*tp_itemsize*/
  (destructor)tiling_dealloc,                  /*tp_dealloc*/
  0,                                           /*tp_print*/
  0,                                           /*tp_getattr*/
  0,                                           /*tp_setattr*/
  0,                                           /*tp_compare*/
  0,                                           /*tp_repr*/
  0,                                           /*tp_as_number*/
  0,                                           /*tp_as_sequence*/
  0,                                           /*tp_as_mapping*/
  0,                                           /*tp_hash*/
  0,                                           /*tp_call*/
  0,                                           /*tp_str*/
  0,                                           /*tp_getattro*/
  0,                                           /*tp_setattro*/
  0,                                           /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,    /*tp_flags*/
  0,                                           /*tp_doc*/
  0,                                           /*tp_traverse*/
  0,                                           /*tp_clear*/
  0,                                           /*tp_richcompare*/
  offsetof (PyGObject, weakreflist),           /*tp_weaklistoffset*/
  0,                                           /*tp_iter*/
  0,                                           /*tp_iternext*/
  tiling_methods,                              /*tp_methods*/
  0,                                           /*tp_members*/
  0,                                           /*tp_getset*/
  0,                                           /*tp_base*/
  0,                                           /*tp_dict*/
  0,                                           /*tp_descr_get*/
  0,                                           /*tp_descr_set*/
  offsetof (PyGObject, inst_dict),             /*tp_dictoffset*/
  tiling_init,                                 /*tp_init*/
  PyType_GenericAlloc,                         /*tp_alloc*/
  PyType_GenericNew,                           /*tp_new*/
  0                                            /*tp_free*/
};


static void
tiling_register_classes (PyObject *obj)
{
  PyObject *module;

  if ((module = PyImport_ImportModule ("gtk")) != NULL) {
    PyObject *moddict = PyModule_GetDict (module);

    _PyGtkImage_Type = (PyTypeObject *) PyDict_GetItemString (moddict, "Image");
    if (_PyGtkImage_Type == NULL) {
      PyErr_SetString (PyExc_ImportError, "cannot import name Image from gtk");
      return;
    }

  } else {
    PyErr_SetString(PyExc_ImportError, "could not import gtk");
    return;
  }

  pygobject_register_class (obj, "Tiling", GTK_TYPE_IMAGE, &t_tiling,
                            Py_BuildValue ("(O)", &PyGtkImage_Type));
}


void
inittiling (void)
{
  PyObject *module, *dict;

  init_pygobject ();

  module = Py_InitModule ("tiling", tiling_functions);
  dict = PyModule_GetDict (module);

  tiling_register_classes (dict);

  if (PyErr_Occurred ())
    Py_FatalError ("can't initialise module tiling");
}

