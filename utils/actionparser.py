#
# Parser for action strings.
#
# Grammar:
# ========
# S     -> CALL | CALL , S
# CALL  -> id : call ARGS | call ARGS
# ARGS  -> (ARGS') | () | e
# ARGS' -> arg | arg , ARGS'
#


def parse(rest):

    cmds = []
    while (rest):
        cmd, rest = _parse_command(rest)
        cmds.append(cmd)
    #end while

    return cmds



def _parse_command(cmd):

    inf = len(cmd) + 1
    index1 = cmd.find("(")
    if (index1 == -1): index1 = inf
    index2 = cmd.find(",")
    if (index2 == -1): index2 = inf

    index = min(index1, index2)
    parts, rest = cmd[:index], cmd[index:]
    if (":" in parts):
        ident, call = parts.split(":")
    else:
        ident, call = None, parts

    if (rest and rest[0] == "("):
        args, rest = _parse_args(rest)
    else:
        args = []

    index = rest.find(",")
    if (index != -1): rest = rest[index + 1:]

    if (ident): ident = ident.strip()
    call = call.strip()
    return ((ident, call, args), rest)



def _parse_args(rest):

    args = []
    while (rest and rest[0] != ")"):
        arg, rest = _parse_arg(rest[1:])
        if (arg): args.append(arg)
    #end while

    return (args, rest[1:])



def _parse_arg(cmd):

    # states are: 0 none
    #             1 read " string
    #             2 escape "
    #             3 read ' string
    #             4 escape '
    #             5 escape

    arg = ""
    state = 0
    for pos in xrange(len(cmd)):
        c = cmd[pos]
        if (state == 0):
            if (c == "\""): arg += c; state = 1
            elif (c == "'"): arg += c; state = 3
            elif (c == "\\"): arg += c; state = 5
            elif (c == ","): break
            elif (c == ")"): break
            else: arg += c
        elif (state == 1):
            if (c == "\""): arg += c; state = 0
            elif (c == "\\"): arg += c; state = 2
            else: arg += c
        elif (state == 2): arg += c; state = 1
        elif (state == 3):
            if (c == "'"): arg += c; state = 0
            elif (c == "\\"): arg += c; state = 4
            else: arg += c
        elif (state == 4): arg += c; state = 3
        elif (state == 5): arg += c; state = 0
        #end if
    #end for
    if (state != 0): print "Error"

    rest = cmd[pos:]
    arg = arg.strip().replace("\\,", ",").replace("\\)", ")")
    return (arg, rest)
