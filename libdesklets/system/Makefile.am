INCLUDES = \
	$(GLIBTOP_CFLAGS) \
	$(PYTHON_CFLAGS)

installdir = ${coredir}/libdesklets/system
install_DATA = \
	__init__.py \
	Arch.py \
	ArchFactory.py \
	CPU.py \
	Device.py \
	Net.py \
	Swap.py

install_PYTHON = $(install_DATA)

install_LTLIBRARIES = gtop.la

SUBDIRS = \
	Linux \
	FreeBSD \
	NetBSD \
	OpenBSD


gtop_la_LDFLAGS = -module -avoid-version -as-needed
gtop_la_LIBADD = $(GLIBTOP_LIBS)
gtop_la_SOURCES = gtop.c


EXTRA_DIST = $(install_DATA) gtop.c

CLEANFILES = *.pyc

