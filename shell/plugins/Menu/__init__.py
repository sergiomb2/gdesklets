from shell.Plugin import Plugin

import gtk


#
# Plugin for the menu bar. The bar can easily be extended through other plugins
# by putting items into the menu tree.
#
class UI_Menu(Plugin):


    def init(self):
        self.__menu_tree = []
        self.__menu_bar = gtk.MenuBar()
        self.__menu_bar.show()

        self.__widget = self.__menu_bar

        shell = self._get_plugin("UI_Shell")
        shell.set_menu(self.__widget)



    #
    # Returns the parent node and the index of the node of the given path.
    #
    def __get_node(self, path):

        parts = path.split("/")
        parent = [("", self.__menu_bar, self.__menu_tree)]
        index = 0

        itempath = ""
        for p in parts:
            nil, nil, parent = parent[index]
            if (not p):
                index = len(parent)
            else:
                index = 0
                found = False
                for cname, nil, children in parent:
                    if (cname == p):
                        found = True
                        break
                    index += 1
                #end for
                if (not found):
                    self.insert(itempath, p)
                    return self.__get_node(path)
                
            itempath += p + "/"
            #end if
        #end for

        return (parent, index)


    #
    # Sets the given node to contain the given item.
    #
    def __set_node(self, path, item):

        tmp = path.split("/")
        tmp.pop()
        ppath = "/".join(tmp)
        if (not ppath):
            submenu = self.__menu_bar
        else:
            parent, index = self.__get_node(ppath)
            nil, pitem, nil = parent[index]
            submenu = pitem.get_submenu()

            if (not submenu):
                submenu = gtk.Menu()
                pitem.set_submenu(submenu)

        parent, index = self.__get_node(path)
        name, nil, children = parent[index]
        parent[index] = (name, item, children)
        submenu.insert(item, index)
        


    #
    # Inserts the given node into the tree as an empty node.
    #
    def insert(self, path, name):

        parent, index = self.__get_node(path)
        parent.insert(index + 1, (name, None, []))
        


    #
    # Returns the children of the given node.
    #
    def list(self, path):

        if (path[-1] != "/"): path += "/"
        parent, index = self.__get_node(path)
        ret = []
        for name, nil, nil in parent:
            ret.append(name)

        return ret


    #
    # Sets the given node to be an insertion slot.
    #
    def set_slot(self, path):

        item = gtk.MenuItem()
        return self.__set_node(path, item)



    #
    # Sets the given node to be a plain menu item.
    #
    def set_item(self, path, icon, label, callback, *args):

        if (icon):
            if (not label):
                item = gtk.ImageMenuItem(icon)
            else:
                img = gtk.Image()
                if (icon.startswith("gtk") or icon.startswith("gnome")):
                    img.set_from_stock(icon, gtk.ICON_SIZE_MENU)
                else:
                    img.set_from_file(icon)
                item = gtk.ImageMenuItem(label)
                item.set_image(img)
        else:
            item = gtk.MenuItem(label)

        item.show()
        if (callback):
            def f(*nil): callback(*args)
            item.connect("activate", f)

        self.__set_node(path, item)



    #
    # Sets the given node to be a separator.
    #
    def set_separator(self, path):

        item = gtk.MenuItem()
        item.show()
        return self.__set_node(path, item)



    #
    # Sets the given node to be a checkbox menu item.
    #
    def set_check_item(self, path, label, callback, *args):

        item = gtk.CheckMenuItem(label)
        item.show()
        if (callback):
            def f(*nil): callback(*args)
            item.connect("activate", f)

        return self.__set_node(path, item)



    #
    # Sets the checked state of a checkbox.
    #
    def set_checked(self, path, value):

        parent, index = self.__get_node(path)
        nil, item, nil = parent[index]
        item.set_active(value)



    #
    # Removes the given node from the menu tree.
    #
    def remove_item(self, path):

        tmp = path.split("/")
        tmp.pop()
        ppath = "/".join(tmp)
        if (not ppath):
            submenu = self.__menu_bar
        else:
            parent, index = self.__get_node(ppath)
            nil, pitem, nil = parent[index]
            submenu = pitem.get_submenu()

            if (not submenu):
                submenu = gtk.Menu()
                pitem.set_submenu(submenu)

        parent, index = self.__get_node(path)
        name, item, nil = parent[index]
        if (item):
            submenu.remove(item)
        del parent[index]
    

def get_class(): return UI_Menu
