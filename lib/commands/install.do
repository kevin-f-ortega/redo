#!/bin/sh -e

# ----------------------------------------------------------------------
# install.do
# Install redo command implementations
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set INSTALL LIBDIR

subdir=`basename $DIR`
evald $INSTALL -d $LIBDIR

for py in *.py
do
	evald $INSTALL -m 0644 $py $LIBDIR/$py
done
