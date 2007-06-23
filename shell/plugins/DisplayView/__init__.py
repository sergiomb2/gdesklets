from shell.Plugin import Plugin

import gtk


#
# View for browsing the installed desklets.
#
class View_Displays(Plugin):

    def activate(self):

        #self._get_plugin("UI_Bookmarks").show()
        self._get_plugin("UI_DisplayBrowser").show()


    def deactivate(self):

        #self._get_plugin("UI_Bookmarks").hide()
        self._get_plugin("UI_DisplayBrowser").hide()


    def get_name(self):

        return "Displays"



    def get_icon(self):

        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_SMALL_TOOLBAR)
        img.show()
        
        return img


    def get_priority(self): return 0
    

def get_class(): return View_Displays
