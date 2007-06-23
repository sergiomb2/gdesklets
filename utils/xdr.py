"""
This module implements a simple tuple transmission protocol. It's kept simple
to be implementable in other languages as well.

The protocol can only transmit lists of strings, which it splits up into chunks.
A chunk consists of a LENGTH byte, the actual PAYLOAD, and a STATUS byte.

A single string is split up into several chunks if it exceeds the maximum length
which can be specified by the LENGTH byte (255), otherwise a string is one
chunk.

The STATUS byte after every chunk tells if the chunk is

 - continued in the next chunk (CONT)
 - the last chunk of a string (NEXT)
 - the last chunk in the transmission (END)

In order to handle empty lists without getting too complicated, all lists are
extended by an arbitrary first element which just gets ignored.


Example:

  ["Hello", "World!"] is transmitted as:

  01  00 01   05   48 65 6C 6C 6F 01   06  57 6F 72 6C 64 21 02

  (1) ?  NEXT (5)  H  e  l  l  o  NEXT (6) W  o  r  l  d  !  END
"""


class XDRError(RuntimeError):
    pass


_SEND_ERROR = "--SEND ERROR--"


_CONT = chr(0)
_NEXT = chr(1)
_END  = chr(2)


def send(s, *args):

    args = ["\0"] + list(args)
    while (args):
        a = args.pop(0)

        chunks = [ a[i:i + 0xff] for i in range(0, len(a), 0xff) ]
        while (chunks):
            c = chunks.pop(0)
            s.send(chr(len(c)))
            s.send(c)
            if (chunks): s.send(_CONT)

        if (args): s.send(_NEXT)

    s.send(_END)


def send_error(s):

    send(s, _SEND_ERROR)


def recv(s):

    args = []
    chunk = ""
    while (True):
        try:
            length = ord(s.recv(1))
        except:
            raise XDRError

        if (length): chunk += s.recv(length)

        flag = s.recv(1)
        if (flag == _CONT): continue

        args.append(chunk)
        chunk = ""

        if (flag == _END): break
    #end while

    return args[1:]
