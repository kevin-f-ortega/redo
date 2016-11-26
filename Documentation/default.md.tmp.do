#!/bin/sh -e 

# ----------------------------------------------------------------------
# default.md.tmp.do
# ----------------------------------------------------------------------

. ./defs.sh

redo-ifchange $REDO_ROOT/lib/version/vars $2.md
. ../version/vars
sed -e "s/%VERSION%/$TAG/" -e "s/%DATE%/$DATE/" $2.md
