import gobject
import gtk


class Downloader(gtk.Dialog):

    def __init__(self, path):

        self.__is_cancelled = False

        gtk.Dialog.__init__(self, title = "", buttons = (gtk.STOCK_CANCEL,
                                                         gtk.RESPONSE_CANCEL))
        self.set_default_size(300, 100)
        self.connect("response", self.__on_cancel)

        vbox = self.vbox

        hbox = gtk.HBox(False, 12)
        hbox.set_border_width(12)
        vbox.pack_start(hbox, True, True)
        import os
        img = gtk.Image()
        img.set_from_file(os.path.join(path, "download.png"))
        hbox.pack_start(img, False, False)

        vbox = gtk.VBox()
        hbox.pack_end(vbox, True, True)

        lbl = gtk.Label("<b>" + _("Retrieving:") + "</b>")
        lbl.set_use_markup(True)
        align = gtk.Alignment(0.0, 0.0)
        align.add(lbl)
        vbox.add(align)

        self.__label = gtk.Label("")
        self.__label.set_use_markup(True)
        align = gtk.Alignment(0.0, 0.0)
        align.add(self.__label)
        vbox.add(align)

        self.__bar = gtk.ProgressBar()
        vbox.add(self.__bar)


    def __on_cancel(self, src, response):

        self.__is_cancelled = True


    def download(self, url, dest):

        name = url
        if (len(name) >= 60):
            name = name[:30] + "..." + name[-30:]
        gobject.timeout_add(0, self.__label.set_text, "%s" % (name))
        gobject.timeout_add(0, self.__bar.set_fraction, 0)
        gobject.timeout_add(0, self.__bar.set_text, "Contacting...")

        gobject.timeout_add(0, self.show_all)
        self.__is_cancelled = False

        dest_fd = open(dest, "w")

        import gconf
        client = gconf.client_get_default()
        use_proxy = client.get_bool('/system/http_proxy/use_http_proxy')
        if (use_proxy != 0):
           host = client.get_string('/system/http_proxy/host')
           port = client.get_int('/system/http_proxy/port')
           if (host != ""):
               http_proxy = "http://" + host + ':' + str(port)
           else:
               http_proxy = None
        else:
            http_proxy = None

        import urllib2

        if (http_proxy is not None):
            proxy_support = urllib2.ProxyHandler({"http" : http_proxy})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)

        src_fd = urllib2.urlopen(url)
        total_size = src_fd.info().get("Content-Length", 0)
        so_far = 0
        while (not self.__is_cancelled):
            data = src_fd.read(4096)
            if (not data):
                break
            dest_fd.write(data)
            so_far += len(data)
            value = (100 * so_far / max(0.1, float(total_size)))
            gobject.timeout_add(0, self.__bar.set_fraction, value / 100.0)
            gobject.timeout_add(0, self.__bar.set_text, "%i%%" % (value))

        src_fd.close()
        dest_fd.close()

        gobject.timeout_add(0, self.hide)

