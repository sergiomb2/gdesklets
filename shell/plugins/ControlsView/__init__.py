from shell.Plugin import Plugin

import gtk


#
# View for managin controls.
#
class View_Controls(Plugin):

    def activate(self):

        self._get_plugin("UI_ControlBrowser").show()


    def deactivate(self):

        self._get_plugin("UI_ControlBrowser").hide()


    def get_name(self):

        return "Controls"


    def get_icon(self):

        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        img.show()
        
        return img


    def get_priority(self): return 10
    

def get_class(): return View_Controls
