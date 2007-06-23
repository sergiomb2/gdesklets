def create_arch():

    arch = __detect_arch()
    arch._init()
    return arch


def __detect_arch():

    import os
    uname = os.uname()

    if (uname[0] == 'Linux'):

        import Linux

        if (uname[-1] in ('i386', 'i486', 'i586', 'i686', 'athlon', 'x86_64')):
            return Linux.X86()

        if (uname[-1] in ('sparc', 'sparc64')):
            return Linux.Sparc()

        if (uname[-1] in ('ppc', 'ppc64')):
            return Linux.PPC()

        return Linux.Generic()


    elif (uname[0] == 'FreeBSD'):

        import FreeBSD

        return FreeBSD.Generic()


    elif (uname[0] == 'OpenBSD'):

        import OpenBSD

        return OpenBSD.Generic()


    elif (uname[0] == 'NetBSD'):

        import NetBSD

        return NetBSD.Generic()

    elif (uname[0] == 'SunOS'):

        import Solaris
        r = os.popen('/usr/bin/uname -p').read()
        if (r[:-1] in ('i386')):
            return Solaris.X86()

        if (r[:-1] in ('sparc')):
            return Solaris.Sparc()

        return Solaris.Generic()

    log("OS/Architecture not found!")

    import Arch

    return Arch.Arch()

