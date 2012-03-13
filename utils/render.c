#include "render.h"

#include <gdk/gdkx.h>
#include <string.h>
#include <X11/Xlib.h>

static inline void
copy_n_rows (const GdkPixbuf *dest, const gint n,
             const gint row_size, const gint offset)
{
  guchar *pixels = gdk_pixbuf_get_pixels (dest);
  memcpy (pixels + offset, pixels, n * row_size);
}


static void
make_row (const GdkPixbuf *src, GdkPixbuf *dest, const gint offset)
{
  gint    x, y;
  guchar *in, *out;

  const gint src_height     = gdk_pixbuf_get_height (src);
  const gint dest_height    = gdk_pixbuf_get_height (dest);
  const gint src_rowstride  = gdk_pixbuf_get_rowstride (src);
  const gint dest_rowstride = gdk_pixbuf_get_rowstride (dest);

  const gint rstride = gdk_pixbuf_get_width (src) * (
       (gdk_pixbuf_get_n_channels (src) * gdk_pixbuf_get_bits_per_sample (src)
        + 7) / 8);
  const gint q = offset / dest_rowstride;

  in  = gdk_pixbuf_get_pixels (src);
  out = gdk_pixbuf_get_pixels (dest) + offset;

  for (y = 0; (y < src_height) && (y + q < dest_height); y++) {
    for (x = 0; x < dest_rowstride; x += rstride) {
      memcpy (out + x, in, MIN (src_rowstride, dest_rowstride - x) );
    }
    in  +=  src_rowstride;
    out += dest_rowstride;
  }
}


static void
filter_opacity (const GdkPixbuf *pbuf, const gfloat opacity)
{
  guchar *data;
  gint x, y, rowstride, height;

  data  = gdk_pixbuf_get_pixels (pbuf);

  rowstride = gdk_pixbuf_get_rowstride (pbuf);
  height = gdk_pixbuf_get_height (pbuf);
  for (x = 3; x < rowstride; x += 4) {
    for (y = 0; y < height; y++) {
      data[y * rowstride + x] *= opacity;
    }
  }
}

void
render_to_image (GtkImage *image, GdkPixbuf *pbuf,
                 const gint width, const gint height,
                 const gfloat opacity, const gfloat saturation)
{
  GdkPixbuf *scaled;

  const gint srcwidth = gdk_pixbuf_get_width (pbuf);
  const gint srcheight = gdk_pixbuf_get_height (pbuf);

  /* scale pixbuf */
  scaled = gdk_pixbuf_scale_simple (pbuf, width, height, GDK_INTERP_BILINEAR);

// the "original" code, causing Bug #260288 :
/*
  if (srcwidth != width || srcheight != height)
    scaled = gdk_pixbuf_scale_simple (pbuf, width, height, GDK_INTERP_BILINEAR);
  else
    scaled = pbuf;
*/

  /* set opacity */
  filter_opacity (scaled, opacity);

  /* set saturation */
  gdk_pixbuf_saturate_and_pixelate (scaled, scaled, saturation, FALSE);

  /* set image */
  gtk_image_set_from_pixbuf (image, scaled);

// this condition is causing a memory leak since rev. 142
/*
  if (srcwidth != width || srcheight != height)
*/
    g_object_unref (scaled);
}


void
render_tile (const GdkPixbuf *source, GdkPixbuf *destination)
{
  gint row, offset;

  const gint row_width  = gdk_pixbuf_get_rowstride (destination);
  const gint row_height = gdk_pixbuf_get_height (source);
  const gint row_size   = row_width * row_height;
  const gint dest_size  = row_width * gdk_pixbuf_get_height (destination);
  const gint max        = gdk_pixbuf_get_height (destination) / row_height;

  /* first iteration unrolled */
  offset = 0;
  row    = 0;
  make_row (source, destination, offset);
  row++;
  offset += row_size;

  while (offset < dest_size && row < max) {
      const gint n = MIN (row, max - row);
      copy_n_rows (destination, n, row_size, offset);
      row += n;
      offset += row_size * n;
  }

  /* last iteration unrolled */
  make_row (source, destination, offset);
}


void
render_background_fallback (GdkPixbuf *destination,
                            const gint x, const gint y,
                            const gint width, const gint height)
{
  Display *dpy;
  GdkWindow *gdkwin;
  XEvent ev;
  XSetWindowAttributes attrs = { ParentRelative, 0L, 0, 0L, 0, 0, Always,
                                 0L, 0L, False, ExposureMask, 0L, True, 0, 0 };

  /* create overrideredirect window with CopyFromParent at the desired place */
  dpy                = gdk_x11_get_default_xdisplay ();
  const gint screen  = DefaultScreen (dpy);
  const Window src   = XCreateWindow (dpy, RootWindow (dpy, screen), x, y,
                       width, height, 0, CopyFromParent, CopyFromParent,
                       CopyFromParent, CWBackPixmap | CWBackingStore |
                       CWOverrideRedirect | CWEventMask,
                       &attrs);
  XGrabServer (dpy);
  XMapRaised (dpy, src);
  XSync (dpy, False);

  /* wait until the window is visible */
  do
    XWindowEvent (dpy, src, ExposureMask, &ev);
  while (ev.type != Expose);

  /* copy window contents into pixbuf */
  gdkwin = gdk_window_foreign_new (src);
  gdk_pixbuf_get_from_drawable (destination, gdkwin, NULL,
                                0, 0, 0, 0, width, height);

  /* close window and clean up */
  g_object_unref (G_OBJECT (gdkwin));
  XUngrabServer (dpy);
  XDestroyWindow (dpy, src);
}


void
render_background (GdkPixbuf *destination,
                   glong wallpaper_id, gint x, gint y, gint width, gint height)
{

  gint         pwidth, pheight;
  GdkColormap *cmap;
  GdkPixmap   *pmap;

  /* get root window */
  const GdkWindow *rootwin = gdk_get_default_root_window ();
  /* get colormap of root window */
  cmap = gdk_drawable_get_colormap (GDK_DRAWABLE (rootwin));
  /* get pixmap from X server */
  pmap = gdk_pixmap_foreign_new ((GdkNativeWindow) wallpaper_id);
  /* get dimensions */
  gdk_drawable_get_size (GDK_DRAWABLE (pmap), &pwidth, &pheight);

  /* tile wallpaper over pixbuf */
  const gint sx = - (x % pwidth);
  const gint sy = - (y % pheight);
  for (x = sx; x < width; x += pwidth) {
    for (y = sy; y < height; y += pheight) {
      const gint dstx = MAX (0, x);
      const gint dsty = MAX (0, y);
      const gint srcx = dstx - x;
      const gint srcy = dsty - y;
      const gint w = MIN (pwidth - srcx, width - dstx);
      const gint h = MIN (pheight - srcy, height - dsty);
      gdk_pixbuf_get_from_drawable (destination, pmap, cmap, srcx, srcy,
                                    dstx, dsty, w, h);
    }
  }

  g_object_unref (pmap);
}

