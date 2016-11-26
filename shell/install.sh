#!/bin/sh -e

# ----------------------------------------------------------------------
# install.sh
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set LIBDIR

evald $INSTALL -d $LIBDIR

sh sh.sh
evald cp -R sh $LIBDIR/sh
