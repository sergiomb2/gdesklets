import os
import sys
import traceback
import vfs


#
# Class for formatting errors. Hilights the bad line of code.
#
class _ErrorFormatter(object):

    __slots__ = ()

    #
    # Analyzes the given traceback and returns a developer-friendly error
    # output with markups.
    # If code is given, that string of code will be used as the source code,
    # instead of loading it.
    # If lineno is given, that number will be used as the linenumber. Only makes
    # sense together when code is given.
    # If deep_trace is True, the traceback history will be traversed as well.
    #
    def format(self, tb, code = None, lineno = -1, filename = "",
               deep_trace = False):

        # tracebacks are dangerous objects; to avoid circular references,
        # we have to drop references to a traceback ASAP

        # get recent traceback
        exc_type = tb[0]
        exc_value = tb[1]
        exc_tb = tb[2]

        # get filename and lineno
        if (not filename and lineno == -1):
            if (hasattr(exc_value, "filename") and
                  hasattr(exc_value, "lineno")):
                filename = exc_value.filename
                lineno = exc_value.lineno
            else:
                tbs = traceback.extract_tb(exc_tb)
                filename = tbs[-1][0]
                lineno = tbs[-1][1]
                del tbs

        # print error message
        out = "\n"
        out += "[EXC]%s\n" % str(exc_value)

        # dig into the traceback for additional information
        if (deep_trace):
            for trace in traceback.extract_tb(exc_tb):
                cntxt = trace[0]
                lno = trace[1]
                funcname = trace[2]
                out += "in %s: line %d %s\n" % (cntxt, lno, funcname)

        # load code from file if no code was specified
        if (not code):
            # get last traceback (otherwise we would load the wrong file for
            # hilighting)
            this_tb = exc_tb
            while (this_tb.tb_next):
                tmp = this_tb
                del this_tb
                this_tb = tmp.tb_next
                del tmp

            # get the .py file; we don't want .pyc or .pyo!
            path = this_tb.tb_frame.f_globals.get("__file__")
            del this_tb
            if (path and path[-4:-1] == ".py"): path = path[:-1]

            if (path and vfs.exists(path)):
                code = vfs.read_entire_file(path)
                filename = path
        #end if

        del exc_tb

        # find and hilight the bad line of code, while adding handy line numbers
        if (code):
            lines = code.splitlines()
            lno = 1
            for i in range(len(lines)):
                if (lno == lineno):
                    lines[i] = "[ERR]>%4d " % lno + lines[i]
                else:
                    lines[i] = "[---] %4d " % lno + lines[i]
                lno += 1
            #end for

            # take a small chop out of the code
            begin = max(0, lineno - 6)
            part = lines[begin:begin + 12]

            out += "[EXC]%s\n\n" % filename
            out += "\n".join(part)

        else:
            out += "[EXC]%s\n\n" % filename
            out += "[EXC]>> could not load source code for hilighting <<"

        #end if

        return out



#
# We are unable to load the source code if only a relative filename was
# available. Therefore, we have to extend the import handler in order to always
# give us an absolute path.
#
_old_imp = __import__
def _new_imp(*args, **kwargs):

    module = _old_imp(*args, **kwargs)
    # builtin modules have no "__file__" attribute, so we have to check for it
    if (module):
        if (hasattr(module, "__file__")):
            module.__file__ = os.path.abspath(module.__file__)
        return module
    else:
        return ""

import __builtin__
__builtin__.__import__ = _new_imp



_singleton = _ErrorFormatter()
def ErrorFormatter(): return _singleton
