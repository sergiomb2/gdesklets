# Put compiled object files into the same sub-directory as their sources
AUTOMAKE_OPTIONS = 1.7 subdir-objects dist-bzip2

# gettext comes with its own build system
SUBDIRS = po

ACLOCAL_AMFLAGS = -I macros ${ACLOCAL_FLAGS}

installdir = ${coredir}
desktopdir = $(datadir)/applications
autostartdir = $(sysconfdir)/xdg/autostart
sharedmimepackagedir = $(datadir)/mime/packages
mimeicondir = $(datadir)/icons/gnome/48x48/mimetypes
basicdeskletsdir = ${installdir}

include Makefile_gdesklets.am
include Makefile_python.am

# uncomment the following 'include' line if you want to build a full release
# (you will have to copy the desklets-basic to the basedir first !)

# include Makefile_basicdesklets.am

.DELETE_ON_ERROR:
