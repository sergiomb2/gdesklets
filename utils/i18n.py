import os
import gettext
import sys


def find_locale_dir():

    fullpath = os.path.abspath(sys.argv[0])
    d, f = os.path.split(fullpath)

    if f == 'gdesklets':
        # we're in $prefix/bin/
        return os.path.join(d, os.pardir, 'share', 'locale')

    elif f in ('gdesklets-daemon', 'gdesklets-shell', 'gdesklets-logview'):
        # we're in $prefix/lib/gdesklets
        return os.path.join(d, os.pardir, os.pardir, 'share', 'locale')


def Translator(domain):
    try:
        localedir = find_locale_dir()
        return gettext.translation(domain, localedir).gettext
    except IOError:
        return lambda s: s
