desktopdir = $(datadir)/applications
desktop_in_files = gdesklets.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

sharedmimedir = $(datadir)/mime
sharedmimepackagedir = $(sharedmimedir)/packages
sharedmimepackage_in_files = gdesklets.xml.in
sharedmimepackage_DATA = $(sharedmimepackage_in_files:.xml.in=.xml)
@INTLTOOL_XML_RULE@

mimeicondir = $(datadir)/icons/gnome/48x48/mimetypes
mimeicon_DATA = gnome-mime-application-x-gdesklets-display.png

pixmapdir = $(PIXMAPDIR)
pixmap_DATA = gdesklets.png

fakepixmapdir = $(coredir)/data

CLEANFILES = \
	$(desktop_DATA)           \
	$(sharedmimepackage_DATA)

installdir = ${coredir}/data
install_DATA = \
	about.png \
	gdesklets.png

EXTRA_DIST = \
	about.png                               \
	gdesklets.desktop                       \
	gdesklets.desktop.in                    \
	gdesklets.png                           \
	gdesklets.xml                           \
	gdesklets.xml.in                        \
	gnome-mime-application-x-gdesklets-display.png

# UGLY hack - where is my brown paperbag?
# We need a pixmapdir relative to the main python script so that the beast can
# be run from our source tree without modification
install-data-hook:
	if test '!' -d $(DESTDIR)$(fakepixmapdir); then \
	    $(mkinstalldirs) $(DESTDIR)$(fakepixmapdir);\
	    chmod 0755 $(DESTDIR)$(fakepixmapdir);      \
	fi

	$(LN_S) -f $(pixmapdir)/gdesklets.png \
	$(DESTDIR)$(fakepixmapdir)/gdesklets.png;

	if test -n "$(UPDATE_MIME_DATABASE)"; then \
	    $(UPDATE_MIME_DATABASE) "$(DESTDIR)${sharedmimedir}"; \
	fi;
	if test -n "$(UPDATE_DESKTOP_DATABASE)"; then \
	    $(UPDATE_DESKTOP_DATABASE) "$(DESTDIR)${desktopdir}"; \
	fi;

uninstall-local: uninstall-desktopDATA uninstall-sharedmimepackageDATA
	if test -n "$(UPDATE_MIME_DATABASE)"; then \
	    $(UPDATE_MIME_DATABASE) "$(DESTDIR)${sharedmimedir}"; \
	fi;
	if test -n "$(UPDATE_DESKTOP_DATABASE)"; then \
	    $(UPDATE_DESKTOP_DATABASE) "$(DESTDIR)${desktopdir}"; \
	fi;

