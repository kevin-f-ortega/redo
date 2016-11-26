# ----------------------------------------------------------------------
# install.do
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set LIBDIR

redo sh
evald $INSTALL -d $LIBDIR
evald cp -R sh $LIBDIR/sh
