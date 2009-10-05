## Process this file with automake to produce Makefile.in

AUTOMAKE_OPTIONS = 1.7 dist-bzip2

SUBDIRS = \
	Controls	\
	Sensors		\
	config		\
	data		\
	doc		\
	display		\
	factory		\
	layout		\
	main		\
	plugin		\
	po		\
	scripting	\
	sensor		\
	shell		\
	utils		\
	libdesklets

EXTRA_DIST = \
	AUTHORS			\
	COPYING			\
	README			\
	TODO			\
	NEWS			\
	autogen.sh		\
	intltool-extract.in	\
	intltool-merge.in	\
	intltool-update.in	\
	ctrlinfo		\
	gdesklets		\
	gdesklets-daemon	\
	gdesklets-logview	\
	contrib/gdesklets-migration-tool \
	contrib/gdesklets.desktop \
	contrib/bash/gdesklets \
	gdesklets-shell		\
	test-control.py

CLEANFILES = \
	intltool-extract	\
	intltool-merge		\
	intltool-update

installdir = ${coredir}
install_SCRIPTS = ctrlinfo gdesklets gdesklets-daemon gdesklets-logview contrib/gdesklets-migration-tool gdesklets-shell test-control.py

install-data-hook:
	if test '!' -d $(DESTDIR)$(bindir); then \
		$(mkinstalldirs) $(DESTDIR)$(bindir); \
		chmod 0755 $(DESTDIR)$(bindir); \
	fi

	$(INSTALL_SCRIPT) gdesklets $(DESTDIR)${coredir}/gdesklets; \
	$(LN_S) -f ${coredir}/gdesklets $(DESTDIR)$(bindir)/gdesklets;
