#include "filter.h"


void
filter_opacity (const GdkPixbuf *pbuf, gfloat opacity)
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
filter_saturation (GdkPixbuf *pbuf, gfloat saturation)
{
    gdk_pixbuf_saturate_and_pixelate (pbuf, pbuf, saturation, FALSE);
}
