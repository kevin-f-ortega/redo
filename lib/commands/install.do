#!/bin/sh -e

# ----------------------------------------------------------------------
# install.do
# Install redo lib files
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

vars_require_set INSTALL LIBDIR

evald $INSTALL -d $LIBDIR/commands

for src in *.py
do
	dest=`echo $src | sed 's,-,_,g'`
	evald $INSTALL -m 0644 $src $LIBDIR/commands/$dest
done
touch $LIBDIR/commands/__init__.py
