#include "render.h"
#include "utils.h"

/* type of TImage */
typedef struct {
  GObject *obj;
  PyObject *inst_dict;
  PyObject *weakreflist;
  GSList *closures;
  guint width;
  guint height;
  gboolean invalidated;
  GdkPixbuf *pbuf;
} TImage;

#define TIMAGE(object) ((TImage *) object)

/* Declare entry point for python */
PyMODINIT_FUNC inittiling (void);


static PyObject *
get_size (PyObject *self)
{
  return Py_BuildValue ("(ii)", gdk_pixbuf_get_width (TIMAGE (self)->pbuf),
                                gdk_pixbuf_get_height (TIMAGE (self)->pbuf));
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
    PyErr_SetString (PyExc_RuntimeError, error->message);
    g_error_free (error);
    return NULL;
  }
  if (!gdk_pixbuf_loader_close (loader, &error)) {
    PyErr_SetString (PyExc_RuntimeError, error->message);
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
  if (!G_UNLIKELY (TIMAGE (self)->pbuf = gdk_pixbuf_new_from_file (filename,
                                                                   &error)))
  {
    PyErr_SetString(PyExc_RuntimeError, error->message);
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
  const guint width, height;
  const gfloat opacity, saturation;

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
  const guint width, height;
  GdkPixbuf *background;

  if (!PyArg_ParseTuple (args, "ii", &width, &height))
    return NULL;

  if (G_UNLIKELY (width == 0 || height == 0)) {
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
  const guint x, y, width, height;
  const glong wallpaper_id;

  if (!PyArg_ParseTuple (args, "liiii", &wallpaper_id, &x, &y, &width, &height))
    return NULL;

  if (G_UNLIKELY (width == 0 || height == 0)) {
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


PyMODINIT_FUNC
inittiling (void)
{
  static PyMethodDef tiling_methods[] = {
    {"get_size", get_size, METH_NOARGS, NULL},
    {"set_from_color", set_from_color, METH_VARARGS, NULL},
    {"set_from_data", set_from_data, METH_VARARGS, NULL},
    {"set_from_file", set_from_file, METH_VARARGS, NULL},
    {"set_from_drawable", set_from_drawable, METH_VARARGS, NULL},
    {"set_from_background", set_from_background, METH_VARARGS, NULL},
    {"tile", tile, METH_VARARGS, NULL},
    {"render", render, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
  };

  module = Py_InitModule ("tiling", (PyMethodDef *) tiling_methods);
  dict = PyModule_GetDict (module);

  if (PyErr_Occurred ())
    Py_FatalError ("Can't initialise module tiling");
}

