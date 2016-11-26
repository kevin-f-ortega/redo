#!/bin/sh -e

# ----------------------------------------------------------------------
# install.do
# Install documentation
# ----------------------------------------------------------------------

. ./defs.sh

vars_require_set INSTALL MANDIR

redo-ifchange all

evald $INSTALL -d $MANDIR/man1

for file in `find . -mindepth 1 -maxdepth 1 -name '*.1'`
do
	evald $INSTALL -m 0644 $file $MANDIR/man1
done
