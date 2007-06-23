# Thanks to Alexandre Duret-Lutz
# http://mail.gnu.org/archive/html/automake/2003-09/msg00031.html 
AC_DEFUN([CHECK_PYTHON_INCLUDE], 
 [AM_PATH_PYTHON([2.0])
  AC_CACHE_CHECK([for $PYTHON include directory],
    [cv_python_inc],
    [cv_python_inc=`$PYTHON -c "from distutils import sysconfig; print sysconfig.get_python_inc()" 2>/dev/null`])
  AC_SUBST([PYTHONINC], [$cv_python_inc])])
