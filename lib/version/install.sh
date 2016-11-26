#!/bin/sh -e

# ----------------------------------------------------------------------
# install.sh
# Install version
# ----------------------------------------------------------------------

. ./defs.sh

redo-ifchange all

evald "$INSTALL -d $LIBDIR/version"

for src in *.py
do
	dest=`echo $src | sed 's,-,_,g'`
	evald "$INSTALL -m 0644 $src $LIBDIR/version/$dest"
done
evald "python -mcompileall $LIBDIR/version"
