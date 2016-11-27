#!/bin/sh -e

# ----------------------------------------------------------------------
# install.do
# Install redo lib files
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set INSTALL LIBDIR

evald $INSTALL -d $LIBDIR

for py in *.py
do
	evald $INSTALL -m 0644 $py $LIBDIR/$py
done
evald python -mcompileall $LIBDIR
