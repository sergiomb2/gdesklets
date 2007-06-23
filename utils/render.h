#ifndef __RENDER_H__
#define __RENDER_H__

#include <gtk/gtk.h>
#include <gdk-pixbuf/gdk-pixbuf.h>

void            render_to_image             (GtkImage *image,
                                             GdkPixbuf *pbuf,
                                             gint width, gint height,
                                             gfloat opacity,
                                             gfloat saturation);

void            render_tile                 (const GdkPixbuf *source,
                                             GdkPixbuf *destination);

void            render_background_fallback  (GdkPixbuf *destination,
                                             gint x, gint y,
                                             gint width, gint height);

void            render_background           (GdkPixbuf *destination,
                                             glong wallpaper_id,
                                             gint x, gint y,
                                             gint width, gint height);

#endif
