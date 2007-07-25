INCLUDES =                  \
	$(PYTHON_CFLAGS)    \
	$(X11_CFLAGS)       \
	$(SVG_CFLAGS)       \
	$(TILING_CFLAGS)    \
	$(UTILS_CFLAGS)

installdir = ${coredir}/utils
install_DATA =              \
	__init__.py         \
	BinTree.py          \
	BGWatcher.py        \
	DOM.py              \
	Element.py          \
	ErrorFormatter.py   \
	KeyBinding.py       \
	LogView.py          \
	MetaDataRegistry.py \
	Observable.py       \
	QueryParser.py      \
	TargetSettings.py   \
	Trie.py             \
	WindowSnapper.py    \
	actionparser.py     \
	datatypes.py        \
	dialog.py           \
	error.py            \
	i18n.py             \
	pwstore.py          \
	Struct.py           \
	wallpaper.py        \
	HIGDialog.py        \
	logger.py           \
	typeconverter.py    \
	vfs.py              \
	xdr.py

install_PYTHON = $(install_DATA)

install_LTLIBRARIES = svg.la tiling.la x11.la

svg_la_SOURCES = svg.c utils.c utils.h
svg_la_LIBADD = $(SVG_LIBS)
svg_la_LDFLAGS = -module -avoid-version -as-needed

tiling_la_SOURCES = tiling.c render.c render.h utils.c utils.h
tiling_la_LIBADD = $(TILING_LIBS)
tiling_la_LDFLAGS = -module -avoid-version -as-needed

x11_la_SOURCES = x11.c utils.c utils.h
x11_la_LIBADD = $(X11_LIBS)
x11_la_LDFLAGS = -module -avoid-version -as-needed

EXTRA_DIST = $(install_DATA)

CLEANFILES = *.pyc *.so *.la*

