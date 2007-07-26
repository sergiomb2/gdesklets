#ifndef __RENDER_H__
#define __RENDER_H__

#include <gtk/gtk.h>
#include <gdk-pixbuf/gdk-pixbuf.h>

void            render_to_image            (GtkImage *image,
                                            GdkPixbuf *pbuf,
                                            const gint width,
                                            const gint height,
                                            const gfloat opacity,
                                            const gfloat saturation);

void            render_tile                (const GdkPixbuf *source,
                                            GdkPixbuf *destination);

void            render_background_fallback (GdkPixbuf *destination,
                                            const gint x,
                                            const gint y,
                                            const gint width,
                                            const gint height);

void            render_background          (GdkPixbuf *destination,
                                            glong wallpaper_id,
                                            const gint x,
                                            const gint y,
                                            const gint width,
                                            const gint height);

#endif
