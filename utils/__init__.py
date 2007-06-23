import __builtin__
import errno
import os
import sys
import string
import thread
import threading
import time

from ErrorFormatter import ErrorFormatter

# the identity of the main thread
MAIN_THREAD = thread.get_ident()


__ALPHA36 =  string.digits + string.letters


def _pretty_excepthook(mytype, value, traceb):

    out = "=== Unhandled error! Something bad and unexpected happened. ===\n"
    out += ErrorFormatter().format(tb = (mytype, value, traceb),
                                   deep_trace = True)
    log(out)

sys.excepthook = _pretty_excepthook


#
# Convenient logger.
#
def _log(data, is_warning = False):

    # show warnings only once
    if (is_warning):
        if (data in _warnings_so_far): return
        else: _warnings_so_far[data] = 1


    now = time.strftime("%D-%T", time.localtime(time.time()))
    out = "[" + now + "]==="
    out = "=" * (80 - len(out)) + out + "\n"
    out += data + "\n"
    out = "\n" + out + "\n"

    print >> sys.stderr, out


# set up logger
_warnings_so_far = {}
__builtin__.log = _log


def cimport(module, c_library):

    """
    imports a C library
    """

    try:
        from module import c_library
    except:
        import sys
        #log("could not import %s!") % c_library
        sys.exit(1)


def parse_color(color):

    if (color[0] == "#" and len(color) == 9):
        alpha = int(color[-2:], 16)
        color = color[:-2]
    else:
        alpha = 255

    import gtk
    c = gtk.gdk.color_parse(color)
    return (c.red >> 8, c.green >> 8, c.blue >> 8, alpha)


def radix(n, b):

    """
    Inverse function to int/long.

    int(radix(n, b), b) == n

    @param n: number to print
    @type n: int/long

    @param b: base
    @type b: 2 <= b <= 36

    @return: str representing n in base b
    @rtype: str
    """

    if not 2 <= b <= 36:
        raise ValueError, "base must be in [2; 36]"

    if n == 0:
        return 0

    if n < 0:
        sign = "-"
        n = -n
    else:
        sign = ""

    rep = ""

    while n:
        n, r = divmod(n, b)
        rep += __ALPHA36[r]

    return sign + rep[::-1]


def makedirs(path):

    """Recursive directory creation function

    Returns :
    - True if path has been created
    - False if path already exists

    (Re)Raises an OSError exception if path does not exist and
    cannot be created or if path cannot be accessed"""

    try:
        os.makedirs(path)
        return True

    except OSError, e:

        if e.errno != errno.EEXIST or not os.path.isdir(path):
            raise

        if not os.access(path, os.F_OK | os.R_OK | os.W_OK | os.X_OK):
            raise OSError("[Errno %d] %s: '%s'"
                          %
                          (errno.EACCES,
                           os.strerror(errno.EACCES),
                           path)
                          )

        return False


def _request_call(when_idle, function, *args):
    """
    Runs the given function by a timer. If several calls of that function
    occurred before, only the last one is run. Do not call this function
    directly, instead use one of its wrappers 'request_call' and
    'request_idle_call'.
    """
    assert (function != None)

    import gobject

    def f(tstamp, function, args):
        if (_timestamps[function] > tstamp): return
        else: function(*args)

    tstamp = time.time()
    _timestamps[function] = tstamp
    if (when_idle):
        gobject.idle_add(f, tstamp, function, args)
    else:
        gobject.timeout_add(0, f, tstamp, function, args)


def request_call(function, *args): _request_call(False, function, *args)
def request_idle_call(function, *args): _request_call(True, function, *args)


_timestamps = {}


def run_in_main_thread(function, *args):

    """
    Runs the given function in the main thread.

    @param function:
    @type  function: callable

    @param *args: arguments
    """

    import gobject

    if (thread.get_ident() == MAIN_THREAD):
        try:
            return function(*args)
        except Exception, exc:
            log("Warning: %s(%s) has raised an exception while running in "
                "main thread.\nThe error was:\n%s" % (function, args, exc))
            import traceback; traceback.print_exc()
            return

    else:
        event = threading.Event()
        result = [None]

        def tmout():
            try:
                result[0] = function(*args)
            except Exception, exc:
                log("Warning: %s(%s) has raised an exception while running in "
                    "main thread.\nThe error was:\n%s" % (function, args, exc))

            event.set()

        gobject.timeout_add(0, tmout)

        event.wait()
        return result[0]


def run_nonblocking(function, *args):
    """
      Runs the given function in a new thread while the main thread waits in
      a nonblocking way, i.e. runs the GTK mainloop.
      If the given function throws an exception, that exception is rethrown by
      this function so that it doesn't get lost.
    """

    def worker(function, event, retval, *args):

        success = False
        try:
            ret = function(*args)
            success = True
        except:
            ret = sys.exc_value
            success = False

        retval[0] = (success, ret)
        event.set()


    retval = [None]
    event = threading.Event()
    t = threading.Thread(target = worker,
                         args = [function, event, retval] + list(args))
    t.start()

    import gtk
    while (not event.isSet()):
        gtk.threads_enter()
        gtk.mainiteration()
        gtk.threads_leave()
    success, ret = retval[0]

    if (not success):
        raise ret
    else:
        return ret


#
# Bind binds a function with arguments
# e.g.  f_with_arg = Bind(f, arg)  ->  f_with_0() <-> f(arg)
#
#
# Memento on *args
# the * notation expands its right_value
# sum4( *(1, 2, 3, 4) ) <-> sum4(1, 2, 3, 4))
#
#
# Bind also works with n-ary functions (including *args)
#
# >>> def sum4(a, b, c, d): return a + b + c +d
# >>> sum2 = Bind(sum4, 1, 2)
# >>> sum2(3, 4)
# 10
# >>> sum4(1, 2, 3, 4)
# 10
#
# Bind makes you able to call a function with some fixed arguments, without
# writing them. It can help you to shadow something.
# "string".lower() is in fact a str instance bound to strobject.lower
# "string".lower() <-> str.lower("string")
#
#
# Note on implementation :
# Bind is implemented with lambda expression because they are faster than
# functions.
# We want to call bound_f = Bind(f, bound_arg0, bound_args1, ...)
# so the first lambda expression at the upper level takes two arguments
# f and its arguments (as an arguments list so it can fit everywhere)
# What we want is to hide bound_args, so we have to return a lambda
# i.e a callable object that only takes arguments.
# At last, the body of the expression that will be evaluated it simple :
# We want to call f with its bound_args and with additional args
# bound_args and args are both tuples, so we just concatenate them (+)
# then we restore the call semantic (*)

# Bind = lambda f, *bound_args : lambda *args : f(* (bound_args + args) )

def Bind(f, *bound_args):

    def helper(*args):
        return f(* (bound_args + args) )

    return helper

#
# The idea behind FakeSelf is to provide member function call syntax for
# non-member function.
# self.attribute = FakeSelf(f, arg)
# self.attribute(extra) <-> f(arg, extra)
# so we have to remove the first argument self, in order to call f.
#
# FakeSelf also provides binding
#
# Note on implementation:
# FakeSelf looks like Bind except that the inner lambda has a first extra argument
# self, that is ignored.
#
# NB:
# FakeSelf can be implemented using Bind
# FakeSelf = lambda f, *bound_args : Bind( lambda self, *args : f(*args), *bound_args)


# FakeSelf = lambda f, *bound_args : lambda self, *args : f(* (bound_args + args) )

def FakeSelf(f, *bound_args):

    def helper(self, *args):
        return f(* (bound_args + args) )

    return helper

