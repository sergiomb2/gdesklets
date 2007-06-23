from shell.Plugin import Plugin
from main import USERHOME
from utils import dialog
from Package import Package
from Downloader import Downloader

import gobject
import gtk
import os
import tempfile
import thread


#
# Installer for desklet packages.
#
class Installer_Package(Plugin):

    def init(self):

        self.__downloader = Downloader(self._get_path())

        menu = self._get_plugin("UI_Menu")
        menu.set_separator("File/Slot")
        menu.set_item("File/Slot", gtk.STOCK_OPEN,
                      _("I_nstall remote package..."), self.__on_remote_file)
        menu.set_item("File/Slot", gtk.STOCK_OPEN, _("_Install package..."),
                      self.__on_file_open)




    #
    # Installs from the given URI.
    #
    def install_from(self, path):

        thread.start_new_thread(self.__install_file, (path,))


    def __on_file_open(self):

        def f(fsel, self):
            file = fsel.get_filename()
            fsel.destroy()
            self.install_from(file)

        dialog.fileselector("", f, None, self)


    def __on_remote_file(self):

        def responder(src, response):
            text = src.vbox.get_children()[0].get_children()[-1].get_text()
            if (response == gtk.RESPONSE_ACCEPT):
                if (text):
                    self.install_from(text)
            else:
                src.destroy()

        from utils.HIGDialog import HIGDialog
        dialog = HIGDialog(buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.connect("response", responder)
        dialog.show()
        label = gtk.Label("Please enter a valid URI here")
        label.show()
        entry = gtk.Entry()
        entry.show()

        vbox = dialog.vbox
        hbox = gtk.HBox()
        hbox.show()
        hbox.set_property("spacing", 12)
        hbox.set_property("border-width", 6)
        hbox.pack_start(label)
        hbox.pack_start(entry)
        vbox.pack_start(hbox)


    #
    # Installs the given file.
    #
    def __install_file(self, url):

        if (url.startswith("/")):
            path = url
            is_local = True
        else:
            path = tempfile.mktemp()
            self.__downloader.download(url, path)
            is_local = False

        try:
            pkg = Package(path)
        except IOError:
            gobject.timeout_add(0, dialog.warning, _("Invalid package"),
                                _("The supplied file could not be opened as a "
                                  "package. It is either corrupted or not of "
                                  "the correct file type."))
            return

        display_paths = self.__install_displays(pkg)
        control_paths = self.__install_controls(pkg)
        sensor_paths = pkg.find_sensors()
        pkg.close()
        if (not is_local): os.unlink(path)

        query = ""
        if (display_paths):
            query = "(MATCH 'path' '*/%s/*')" \
                    % (os.path.basename(display_paths[0]))

        if (not display_paths and not control_paths and not sensor_paths):
            gobject.timeout_add(0, dialog.info, _("Installation failed"),
                                _("The package could not be installed because "
                                  "it contained no installable files."))
        else:
            gobject.timeout_add(0, dialog.info, _("Installation complete"),
                                "The package has been installed successfully.")

        collection = self._get_plugin("Core_DisplayCollection")
        displaybrowser = self._get_plugin("UI_DisplayBrowser")
        gobject.timeout_add(0, collection.reload)
        gobject.timeout_add(0, displaybrowser.set_location, query)



    #
    # Installs the displays from the given package.
    #
    def __install_displays(self, pkg):

        dirs = pkg.find_displays()
        for d in dirs:
            os.system("cp -r %s %s/" % (d, os.path.join(USERHOME, "Displays")))
        sensors = pkg.find_sensors()
        for s in sensors:
            os.system("python %s --nomsg" % (s))

        return dirs


    #
    # Installs the controls from the given package.
    #
    def __install_controls(self, pkg):

        import time
        name = str(time.time())
        dirs = pkg.find_controls()
        path = os.path.join(USERHOME, "Controls")
        if (not os.path.exists(path)): os.mkdir(path)
        for d in dirs:
            os.system("cp -r %s %s/"
                      % (d, os.path.join(path, name)))

        return dirs



def get_class(): return Installer_Package
