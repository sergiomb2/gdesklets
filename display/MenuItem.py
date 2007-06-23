#
# Simple class for modifiable and easy to use menu items.
#
class MenuItem(object):

    __slots__ = ("path", "label", "icon", "callback", "args", "active")


    def __init__(self, path, label = None, icon = None,
                 callback = None, args = [], active = True):

        self.path = path
        self.label = label
        self.icon = icon
        self.callback = callback
        self.args = args
        self.active = active
