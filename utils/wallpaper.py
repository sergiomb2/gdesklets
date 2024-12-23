try:
    from utils.TilingImage import TilingImage as Tiling
except ImportError:
    import sys
    log("Could not import tiling module!")
    sys.exit(1)

import gtk


tiling = Tiling()


#
# Restricts the given coordinates to visible values.
#
def _crop_coords(x, y, width, height):

    scrwidth = gtk.gdk.screen_width()
    scrheight = gtk.gdk.screen_height()

    x = min(x, scrwidth - 1)
    y = min(y, scrheight - 1)

    return (x, y, width, height)



#
# Captures the wallpaper image by accessing the background pixmap.
#
def get_wallpaper(widget, x, y, width, height):

    x, y, width, height = _crop_coords(x, y, width, height)
    # get wallpaper
    try:
        pmap_id = get_wallpaper_id()
        widget.set_from_background(pmap_id, x, y, width, height)

    except NotImplementedError:
        widget.set_from_background(0, x, y, width, height)

    widget.render(width, height, 1, 1)



#
# Returns the ID of the background pixmap.
#
def get_wallpaper_id():

    try:
        root = gtk.gdk.get_default_root_window()
        ident = root.property_get("_XROOTPMAP_ID", "PIXMAP")[2][0]
        return long(ident)

    except:
        raise NotImplementedError
