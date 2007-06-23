#ifndef GDESKLETS_UTILS_UTILS_H
#define GDESKLETS_UTILS_UTILS_H

#include <Python.h>

PyTypeObject* gdesklets_get_pygobject_type(void);

int parse_gdk_window(PyObject *object, void *address);
int parse_gdk_pixmap(PyObject *object, void *address);
int parse_gdk_pixbuf(PyObject *object, void *address);
int parse_gtk_image(PyObject *object, void *address);
int parse_gtk_widget(PyObject *object, void *address);

#endif /* GDESKLETS_UTILS_UTILS_H */
