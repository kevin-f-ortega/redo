#!/bin/sh -e

# ----------------------------------------------------------------------
# install.sh
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set INSTALL LIBDIR

evald $INSTALL -d $LIBDIR

for src in *.py
do
	dest=`echo $src | sed 's,-,_,g'`
	evald $INSTALL -m 0644 $src $LIBDIR/$dest
done
evald python -mcompileall $LIBDIR
