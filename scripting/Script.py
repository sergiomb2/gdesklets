from ElementWrapper import ElementWrapper
from ControlWrapper import ControlWrapper
from config.StateSaver import StateSaver, DefaultStateSaver
from Scriptlet import Scriptlet
from display.MenuItem import MenuItem
from utils.ErrorFormatter import ErrorFormatter
from utils import dialog
from layout import Unit
import exceptions
import gobject



_AUTHORIZED_COMMANDS_KEY = "authorized_commands"

#
# Class for inline scripts together with their environment.
#
class Script:

    def __init__(self, dsp_id, dsp_path):

        self.__scriptlets = {}

        # ID of the display
        self.__dsp_id = dsp_id

        # paths of the display
        self.__dsp_path = dsp_path
        import os
        self.__dsp_dir = os.path.dirname(dsp_path) + os.path.sep

        # the state saver
        self.__state_saver = StateSaver(dsp_id)

        # the environment for this script
        self.__environment = {}

        # the list of created control wrappers
        self.__control_wrappers = []

        # flag indicating whether the display has been stopped
        self.__is_stopped = False


        #
        # setup a sandbox environment
        #
        self.__environment["__builtins__"] = None
        self.__environment["__name__"] = "inline"  # required for classes

        # unit constructor and units
        self.__environment["Unit"] = Unit.Unit
        self.__environment["PX"] = Unit.UNIT_PX
        self.__environment["CM"] = Unit.UNIT_CM
        self.__environment["IN"] = Unit.UNIT_IN
        self.__environment["PT"] = Unit.UNIT_PT
        self.__environment["PERCENT"] = Unit.UNIT_PERCENT

        self.__environment["MenuItem"] = MenuItem

        self.__environment["add_timer"] = self.__script_add_timer
        self.__environment["remove_timer"] = self.__script_remove_timer
        self.__environment["get_config"] = self.__script_get_config
        self.__environment["get_control"] = self.__script_get_control
        self.__environment["set_config"] = self.__script_set_config
        self.__environment["get_desklet_path"] = \
            self.__script_get_desklet_path
        self.__environment["sanitize_string"] = \
            self.__script_sanitize_string
        self.__environment["launch"] = self.__script_launch

        # see end of file
        # WTF do we need True/False there? (because they're not yet keywords)
        self.__environment["False"] = False
        self.__environment["True"] = True
        self.__environment["abs"] = abs
        self.__environment["bool"] = bool
        self.__environment["callable"] = callable
        self.__environment["chr"] = chr
        self.__environment["classmethod"] = classmethod
        self.__environment["cmp"] = cmp
        self.__environment["complex"] = complex
        self.__environment["delattr"] = delattr
        self.__environment["dict"] = dict
        self.__environment["divmod"] = divmod
        self.__environment["enumerate"] = enumerate
        self.__environment["float"] = float
        self.__environment["getattr"] = getattr
        self.__environment["hasattr"] = hasattr
        self.__environment["hash"] = hash
        self.__environment["hex"] = hex
        self.__environment["id"] = id
        self.__environment["int"] = int
        self.__environment["isinstance"] = isinstance
        self.__environment["issubclass"] = issubclass
        self.__environment["iter"] = iter
        self.__environment["len"] = len
        self.__environment["list"] = list
        self.__environment["locals"] = locals
        self.__environment["long"] = long
        self.__environment["max"] = max
        self.__environment["min"] = min
        self.__environment["object"] = object
        self.__environment["oct"] = oct
        self.__environment["ord"] = ord
        self.__environment["property"] = property
        self.__environment["range"] = range
        self.__environment["reduce"] = reduce
        self.__environment["repr"] = repr
        self.__environment["round"] = round
        self.__environment["setattr"] = setattr
        self.__environment["staticmethod"] = staticmethod
        self.__environment["str"] = str
        self.__environment["sum"] = sum
        self.__environment["super"] = super
        self.__environment["tuple"] = tuple
        self.__environment["type"] = type
        self.__environment["unichr"] = unichr
        self.__environment["unicode"] = unicode
        self.__environment["vars"] = vars
        self.__environment["xrange"] = xrange
        self.__environment["zip"] = zip

        # exceptions, we need the exceptions
        for name in dir(exceptions):
            if (not name.startswith("_")):
                exc = getattr(exceptions, name)
                self.__environment[name] = exc
        #end for


    #
    # Handles errors in the script.
    #
    def __handle_error(self):

        from utils.error import Error
        Error().handle(self.__dsp_id)


    #
    # Runs a timer in the sandbox. The timer stops when the script is being
    # stopped.
    #
    def __script_add_timer(self, interval, callback, *args):

        def f():
            try:
                if (self.__is_stopped):
                    return False
                else:
                    ret = callback(*args)
                    return ret

            except:
                self.__handle_error()
                return False


        if (type(interval) not in (type(1), type(1.0), type(1L))
              or interval < 0):
            raise UserError(_("Error in add_timer function"),
                           _("\"%s\" isn't a valid integer value!")
                           % `interval`)
            #dialog.warning(_("Error in add_timer function"),
            #               _("\"%s\" isn't a valid integer value!")
            #               % `interval`)
            #return

        return gobject.timeout_add(interval, f)



    #
    # Removes a timer
    #
    def __script_remove_timer(self, ident):

        """ Removes timer with given ID. """

        if gobject.source_remove(ident) is False:
            log(_("Timer identifier '%s' was not found" % ident))



    #
    # Retrieves a configuration value.
    #
    def __script_get_config(self, key, default = None):

        return self.__state_saver.get_key(key, default)



    #
    # Stores a configuration value.
    #
    def __script_set_config(self, key, value):

        self.__state_saver.set_key(key, value)



    #
    # Returns a control readily wrapped for the sandbox.
    #
    def __script_get_control(self, interface, size):

        # FIXME: ensure that this does not break the sandbox
        from factory.ControlFactory import ControlFactory
        factory = ControlFactory()
        ctrl = factory.get_control(interface)
        if (ctrl):
            # created a list of wrapped controls from the template
            wrapped = ControlWrapper(ctrl, size)
            # remember the control wrapper for cleanup on stop()
            self.__control_wrappers.append(wrapped)
            return wrapped

        raise UserError(_("No Control could be found for interface %s") % \
                                                                  (interface,),
                        _("This means that a functionality won't be available "
                          "during execution!"))
        #dialog.warning(_("No Control could be found for interface %s") % \
        #                                                         (interface,),
        #               _("This means that a functionality won't be available "
        #                 "during execution!"))

        #return ""


    #
    # Gets the desklet's path
    #
    def __script_get_desklet_path(self):

        return self.__dsp_dir


    #
    # Sanitizes a string for the XML environment.
    #
    def __script_sanitize_string(self, s):

        sanitized_string = s.replace("&", "&amp;")
        sanitized_string = sanitized_string.replace("<", "&lt;")
        sanitized_string = sanitized_string.replace(">", "&gt;")
        sanitized_string = sanitized_string.replace("\'", "&apos;")
        sanitized_string = sanitized_string.replace("\"", "&quot;")

        return sanitized_string

    #
    # Launches the given command if it's safe.
    #
    def __script_launch(self, command):

        states = DefaultStateSaver()
        permissions = states.get_key(_AUTHORIZED_COMMANDS_KEY, {})

        def run_cmd():
            import os
            os.system(command + " &")

        def run_and_permit():
            permissions[(self.__dsp_id, command)] = True
            states.set_key(_AUTHORIZED_COMMANDS_KEY, permissions)
            run_cmd()


        if ((self.__dsp_id, command) in permissions):
            run_cmd()

        else:
            # FIXME: what is the correct way to escape '=' chars?
            escaped_command = command.replace("=", "")
            escaped_command = escaped_command.replace("\\", "\\\\")
            escaped_command = escaped_command.replace("&", "&amp;")
            escaped_command = escaped_command.replace("<", "&lt;")
            escaped_command = escaped_command.replace(">", "&gt;")

            dialog.question(_("Security Risk"),
                            _("The desklet %(desklet_name)s wants to execute "
                              "a system command:\n"
                              "\n"
                              "     <tt><b>%(cmd)s</b></tt>\n"
                              "\n"
                              "To protect your system from malicious "
                              "programs, you can deny the execution of this "
                              "command.\n"
                              "\n"
                              "If you are sure that the command is harmless, "
                              "you may permanently allow this desklet "
                              "instance to run it.")
                            % {"desklet_name": self.__dsp_path, "cmd": escaped_command},
                            (_("Deny!"), None),
                            (_("Allow once"), run_cmd),
                            (_("Allow for this desklet"), run_and_permit))


    #
    # Stops this scripting object.
    #
    def stop(self):

        self.__is_stopped = True
        del self.__environment

        # delete all wrapped controls
        for w in self.__control_wrappers:
            try:
                w.stop()
            except StandardError, exc:
                import traceback; traceback.print_exc()
                log(_("Could not stop control wrapper %s" % w))
            del w
        del self.__control_wrappers



    #
    # Removes this scripting object and its state.
    #
    def remove(self):

        states = DefaultStateSaver()
        permissions = states.get_key(_AUTHORIZED_COMMANDS_KEY, {})
        for ident, cmd in permissions.keys():
            if (ident == self.__dsp_id): del permissions[(ident, cmd)]
        states.set_key(_AUTHORIZED_COMMANDS_KEY, permissions)

        self.__state_saver.remove()


    #
    # Creates the given namespace if it does not yet exist.
    #
    def __make_namespace(self, namespace):

        class Namespace: pass
        if (not namespace in self.__environment):
            self.__environment[namespace] = Namespace()


    #
    # Adds the given element to the environment. The namespace has to exist.
    # If no namespace is given, the element becomes a member of the global
    # namespace.
    #
    def add_element(self, namespace, name, elem):

        if (namespace): self.__make_namespace(namespace)

        wrapped = ElementWrapper(elem)
        if (not namespace):
            self.__environment[name] = wrapped
        else:
            setattr(self.__environment[namespace], name, wrapped)


    #
    # Same as add_element() but puts elements into a structure of (nested)
    # arrays.
    #
    def add_element_with_path(self, namespace, name, elem, indexpath):

        if (namespace): self.__make_namespace(namespace)

        try:
            if (not namespace):
                lst = self.__environment[name]
            else:
                lst = getattr(self.__environment[namespace], name)
        except:
            lst = []

        if (not namespace):
            self.__environment[name] = lst
        else:
            setattr(self.__environment[namespace], name, lst)

        # build up the structure of (nested) arrays
        for index in indexpath[:-1]:
            while (len(lst) - 1 < index): lst.append([])
            lst = lst[index]
        index = indexpath[-1]
        while (len(lst) - 1 < index): lst.append([])
        lst[index] = ElementWrapper(elem)



    #
    # Fixes the indentation of Python code.
    #
    def __fix_indentation(self, code):

        lines = code.splitlines()
        min_indent = len(code)
        # find the minimal indentation
        for l in lines:
            if (not l.strip()): continue
            this_indent = len(l) - len(l.lstrip())
            min_indent = min(min_indent, this_indent)

        # apply the minimal indentation
        out = ""
        for l in lines:
            out += l[min_indent:] + "\n"

        return out



    #
    # Executes a block of script.
    #
    def execute(self, scriptlet, handle_error = True):

        sid = scriptlet.script_id

        # get the block into shape
        code = self.__fix_indentation(scriptlet.script)

        # remember scriptlet for later
        self.__scriptlets[sid] = scriptlet

        # compile and run
        try:
            from utils.error import Error
            Error().register_code("<inline '%s'>" % sid, code)
            pycode = compile(code, "<inline '%s'>" % sid, 'exec')
            #pycode = compile(code, "%s" % scriptlet.filename, 'exec')
            exec pycode in self.__environment

        except:
            #if (handle_error):
            self.__handle_error()



    #
    # Retrieves the value of the given object from the scripting environment.
    #
    def get_value(self, name):

        if (not name):
            return
        # TODO: if the type of the bound variable differs we have to check it
        cmd = "__retrieve__ = %s" % (name,)
        self.execute(Scriptlet(cmd, "<internal>"), handle_error = False)

        # may raise an exception
        return self.__environment.pop("__retrieve__")



    #
    # Sets the value of the given object in the scripting environment.
    #
    def set_value(self, name, value):

        self.__environment["__inject__"] = value
        cmd = "%s = __inject__" % name
        self.execute(Scriptlet(cmd, "<internal>"), handle_error = False)
        self.__environment.pop("__inject__")



    #
    # Calls the given function in the sandbox.
    #
    def call_function(self, name, *args):

        func = self.get_value(name)
        try:
            func(*args)
        except:
            #log("A function call in the inline script failed.")
            self.__handle_error()



    #BEGIN
    # + 2.3.3 http://python.org/doc/2.3.3/lib/built-in-funcs.html
    #                        vs.
    # - 2.2.3 http://python.org/doc/2.2.3/lib/built-in-funcs.html
    # * dangerous

    # * __import__
    # abs
    # - apply
    # + basestring
    # bool
    # - buffer
    # callable
    # chr
    # classmethod
    # cmp
    # - coerce
    # * compile
    # complex
    # delattr
    # dict
    # dir # ?
    # divmod
    # + enumerate
    # * eval
    # * execfile
    # * file
    # filter # may be should print a warning and a link to list-comprehension
    # float
    # getattr
    # globals # ?
    # hasattr
    # hash
    # help # not very useful
    # hex
    # id
    # - intern
    # input # not very useful
    # int
    # isinstance
    # issubclass
    # iter
    # len
    # list
    # locals
    # long
    # map # maybe should print a warning and a link to list-comprehension
    # max
    # min
    # + object
    # oct
    # * open
    # ord
    # property
    # range
    # raw_input # not very usefull
    # reduce
    # * reload
    # repr
    # round
    # setattr
    # - slice
    # staticmethod
    # str
    # + sum
    # super
    # tuple
    # type
    # unichr
    # unicode
    # vars
    # xrange
    # zip

    # 2.3 Deprecated/Non-essentials functions
    # http://python.org/doc/2.3.3/lib/non-essential-built-in-funcs.html
    # - apply
    # - buffer
    # - coerce
    # - intern
    #END
