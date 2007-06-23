from shell.Plugin import Plugin

import gtk


#
# The switch buttons for the different views.
# Reads the available views from the "views" file.
#
class Shell_ViewSwitch(Plugin):

    def init(self):
        self.__buttons = []
        self.__views = []

        vbox = gtk.VBox(True, 4)
        vbox.set_border_width(4)

        views = self._get_plugins_by_pattern("name", "View_*")

        cnt = 0
        views.sort(lambda x, y: cmp(x.get_priority(), y.get_priority()))
        for view in views:
            #viewname = v.strip()
            #if (not viewname): continue
            
            if (cnt == 0):
                hbox = gtk.HBox(True, 4)
                vbox.add(hbox)

            #view = self._get_plugin(viewname)
            btn = gtk.ToggleButton()
            align = gtk.Alignment(0.5, 0.5)
            btn.add(align)
            bbox = gtk.HBox(False, 2)
            bbox.add(view.get_icon())
            bbox.add(gtk.Label(view.get_name()))
            align.add(bbox)
            
            btn.connect("toggled", self.__on_switch, view)
            self.__buttons.append(btn)
            self.__views.append(view)
            hbox.add(btn)
            cnt += 1
            if (cnt == 2): cnt = 0
        #end for

        self.__buttons[0].set_active(True)
        vbox.show_all()
        self.__widget = vbox

        shell = self._get_plugin("UI_Shell")
        shell.set_switch(self.__widget)



    def __on_switch(self, src, view):

        if (src.get_active()):
            for btn in self.__buttons:
                if (btn != src): btn.set_active(False)

            for v in self.__views:
                if (v != view): v.deactivate()

            view.activate()


def get_class(): return Shell_ViewSwitch
