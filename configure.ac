
dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.53)
AC_INIT([gDesklets], [0.36.4_beta])
AC_CONFIG_SRCDIR([configure.ac])
AM_INIT_AUTOMAKE([dist-bzip2 subdir-objects])
LT_INIT
AM_CONFIG_HEADER([config.h])
AC_CONFIG_MACRO_DIR([macros])
AC_CONFIG_FILES([Makefile])
AM_MAINTAINER_MODE
: ${CFLAGS="-Os -g"}

dnl Required programs
AC_PROG_CC
AM_PROG_CC_C_O
AC_HEADER_STDC
AC_DISABLE_STATIC
IT_PROG_INTLTOOL([0.35.0])
AC_PROG_INSTALL
AC_PROG_LIBTOOL
AC_PROG_LN_S
AC_PROG_MAKE_SET

# Minimum version of Application indicator, made popular in Ubuntu
APPINDICATOR_REQUIRED=0.0.7

AC_ARG_ENABLE(debug,AS_HELP_STRING([--enable-debug],[Maximum debugging]),
              set_debug="$enableval",[set_debug=no])
AC_MSG_CHECKING(for more debugging including macro expansion)
if test "$GCC" = "yes" -a "$set_debug" != "no"; then
  AC_MSG_RESULT(yes)
  CFLAGS="$CFLAGS -O0 -g3"
else
  AC_MSG_RESULT(no)
fi

AC_ARG_ENABLE(more-warnings,AS_HELP_STRING([--enable-more-warnings],[More compiler warnings]),
              set_more_warnings="$enableval",[set_more_warnings=no])

AC_MSG_CHECKING(for more warnings, including -Werror)
if test "$GCC" = "yes" -a "$set_more_warnings" != "no"; then
    AC_MSG_RESULT(yes)
    CFLAGS="$CFLAGS \
    -Wall -Wchar-subscripts -Wmissing-declarations -Wmissing-prototypes \
    -Wmissing-declarations -Wredundant-decls -Wunreachable-code \
    -Wpointer-arith -Wcast-align -Wsign-compare -ansi \
    "
else
    AC_MSG_RESULT(no)
fi

AC_ARG_ENABLE(update-check,
              AS_HELP_STRING([--disable-update-check], [Version update check]),
              [
                AS_IF([test "x$enable_update_check" = "xno"],
                      [enable_update_check=False],
                      [enable_update_check=True])
              ],
              [enable_update_check=True])
AC_SUBST(enable_update_check)

AC_ARG_ENABLE(appindicator,
              AS_HELP_STRING([--enable-appindicator[=@<:@no/auto/yes@:>@]],[Build support for application indicators]),
              [enable_appindicator=$enableval],
              [enable_appindicator="auto"])

if test x$enable_appindicator = xauto ; then
  PKG_CHECK_EXISTS([appindicator-0.1 >= $APPINDICATOR_REQUIRED],
                   enable_appindicator="yes",
                   enable_appindicator="no")
fi

if test x$enable_appindicator = xyes ; then
  appindicator_available=True
  PKG_CHECK_EXISTS([appindicator-0.1 >= $APPINDICATOR_REQUIRED],,
                   AC_MSG_ERROR([appindicator-0.1 is not installed]))
  PKG_CHECK_MODULES(APP_INDICATOR,
                    appindicator-0.1 >= $APPINDICATOR_REQUIRED)
  AC_SUBST(APP_INDICATOR_CFLAGS)
  AC_SUBST(APP_INDICATOR_LIBS)
  AC_DEFINE(HAVE_APP_INDICATOR, 1, [Have AppIndicator])
else
  appindicator_available=False
fi
AM_CONDITIONAL(HAVE_APP_INDICATOR, test x"$enable_appindicator" = xyes)
AC_SUBST(appindicator_available)

AM_PATH_PYTHON([2.4])
PYTHON_PREFIX=`python -c "import sys; print sys.prefix"`
PYTHON_CFLAGS="-I$PYTHON_PREFIX/include/python$PYTHON_VERSION"
AC_CHECK_HEADER([$PYTHON_PREFIX/include/python$PYTHON_VERSION/Python.h],,
    AC_ERROR([Can't find Python.h! You will need python's development package to compile gDesklets.]))
AC_SUBST(PYTHON_CFLAGS)

PKG_CHECK_MODULES(GDESKLETS, pygtk-2.0 >= 2.10.0 pyorbit-2 >= 2.0.1 gnome-python-2.0 >= 2.12.0)
AC_SUBST(GDESKLETS_CFLAGS)
AC_SUBST(GDESKLETS_LIBS)

PKG_CHECK_MODULES(UTILS, glib-2.0 >= 2.10.0 gtk+-2.0 >= 2.10.0 gdk-pixbuf-2.0 >=
2.10.0 pygtk-2.0 >= 2.10.0)
AC_SUBST(UTILS_CFLAGS)
AC_SUBST(UTILS_LIBS)

PKG_CHECK_MODULES(GLIBTOP, pygtk-2.0 >= 2.10.0 libgtop-2.0 >= 2.10.0)
AC_SUBST(GLIBTOP_CFLAGS)
AC_SUBST(GLIBTOP_LIBS)

PKG_CHECK_MODULES(SVG, pygtk-2.0 >= 2.10.0 gtk+-2.0 >= 2.10.0 librsvg-2.0 >= 2.8.0)
AC_SUBST(SVG_CFLAGS)
AC_SUBST(SVG_LIBS)

PKG_CHECK_MODULES(TILING, pygtk-2.0 >= 2.10.0 gtk+-2.0 >= 2.10.0 gdk-pixbuf-2.0 >= 2.10.0)
AC_SUBST(TILING_CFLAGS)
AC_SUBST(TILING_LIBS)

PKG_CHECK_MODULES(X11, pygtk-2.0 >= 2.10.0 gtk+-2.0 >= 2.10.0 gdk-2.0 >= 2.10.0)
AC_SUBST(X11_CFLAGS)
AC_SUBST(X11_LIBS)

GETTEXT_PACKAGE=gdesklets
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT

coredir=${libdir}/gdesklets
AC_SUBST(coredir)

PIXMAPDIR=${datadir}/pixmaps
AC_SUBST(pixmapdir)

localedir=${datadir}/locale
AC_SUBST(localedir)

gnulocaledir=${localedir}
AC_SUBST(gnulocaledir)

AC_OUTPUT([
po/Makefile.in
config/settings.py
])


echo "
=============
Configuration
=============

  gDesklets version: ${VERSION}
  Python prefix:     ${PYTHON_PREFIX}
  Python version:    ${PYTHON_VERSION}

  Install location:  ${prefix}
  Enable warnings:   ${set_more_warnings}
  Enable debugging:  ${set_debug}
  Check for updates: ${enable_update_check}
  App indicator:     ${appindicator_available}
"

