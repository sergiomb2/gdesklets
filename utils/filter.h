#ifndef __FILTER_H__
#define __FILTER_H__

/* Filters are functions which take a pixbuf and some parameters and directly
 * modify that pixbuf's contents.
 */

#include <gdk-pixbuf/gdk-pixbuf.h>

void filter_opacity (const GdkPixbuf *pbuf, gfloat opacity);
void filter_saturation (GdkPixbuf *pbuf, gfloat saturation);

#endif
