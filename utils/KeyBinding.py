import gtk
try:
    import x11
except ImportError:
    import sys
    log("Could not import x11 module!")
    sys.exit(1)


class KeyBinding:
    """
    Class for setting up global desktop keybindings.
    """

    def __init__(self):

        # mapping: (keycode, modifiers) -> action
        self.__action_table = {}

        # proxy widget for receiving events from the root window
        self.__proxy = gtk.Invisible()
        self.__proxy.connect("key-press-event", self.__event_handler)
        self.__proxy.show()



    def __event_handler(self, src, event):

        key = (event.hardware_keycode, event.state)
        action = self.__action_table.get(key)

        if (action): action()



    def bind_key(self, keycode, modifiers, handler):

        self.__action_table[(keycode, modifiers)] = handler
        try:
            x11.grab_ungrab_key(self.__proxy.window, keycode, modifiers, True)
        except RuntimeError, exc:
            print("The following error occurred while binding a key: %s" % exc)


    def unbind_key(self, keycode, modifiers):

        try:
            del self.__action_table[(keycode, modifiers)]
        except KeyError:
            pass

        try:
            x11.grab_ungrab_key(self.__proxy.window, keycode, modifiers, False)
        except:
            pass
