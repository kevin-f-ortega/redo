#!/bin/sh -e

# ----------------------------------------------------------------------
# install.do
# Install redo command implementations
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set INSTALL LIBDIR

subdir=`basename $DIR`
evald $INSTALL -d $LIBDIR/$subdir

for src in *.py
do
	dest=`echo $src | sed 's,-,_,g'`
	evald $INSTALL -m 0644 $src $LIBDIR/$subdir/$dest
done
touch $LIBDIR/$subdir/__init__.py
