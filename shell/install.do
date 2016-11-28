#!/bin/sh -e

# ----------------------------------------------------------------------
# install.do
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set LIBDIR

rm -f $LIBDIR/sh
redo sh
evald $INSTALL -d $LIBDIR
evald cp -R sh $LIBDIR/sh
