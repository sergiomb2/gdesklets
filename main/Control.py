from plugin.Interface import Interface
import utils

import gobject

class Control(object):

    """
    Base class for controls. Every control has to be derived from this class.
    """

    # Warning : this is the only way to escape a Control
    # so be carefull when allowing a method to be called

    AUTHORIZED_METHODS = ('bind', )

    def __init__(self):

        # the handlers for property bindings
        self.__handlers = {}

        # flag indicating whether the control has been stopped
        self.__is_stopped = False

        # the path of the display file (excluding the file)
        self.__display_path = ""
        

    def _update(self, prop):

        """ Issues a change of the given property. """

        lst = self.__handlers.get(prop, [])
        for handler, args in lst:
            try:
                is_callable = hasattr(handler, '__call__')
            except NameError:
                is_callable = False

            if is_callable:
                utils.run_in_main_thread(handler, getattr(self, prop), *args)


    def bind(self, prop, handler, *args):

        """ Binds a handler to property changes. """

        self.__handlers.setdefault(prop, []).append((handler, args))


    def _add_timer(self, interval, callback, *args):

        """ Runs a timer callback at the given intervals. """
        def func(self):
            """ callback function for gobject.timeout_add """
            if self.__is_stopped:
                return False
            return bool(callback(*args))

        return gobject.timeout_add(interval, func, self)


    def _remove_timer(self, ident):

        """ Removes timer with given ID. """

        gobject.source_remove(ident)


    def stop(self):

        """ Stops the control. """

        self.__is_stopped = True
        # remove bound handlers
        self.__handlers.clear()
        self._shutdown()


    def _shutdown(self):

        """
        Shutdown handler for controls. Controls should override this
        method if needed.
        """

        pass


    def __interface(self):

        """
        Returns a description of the interface of this control.
        """

        return Interface.text_describe(self.__class__)

    interface = property(__interface, doc = "Interface description")

