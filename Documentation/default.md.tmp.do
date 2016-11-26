#!/bin/sh -e 

# ----------------------------------------------------------------------
# default.md.tmp.do
# ----------------------------------------------------------------------

. ./defs.sh

redo-ifchange $2.md
sh $REDO_ROOT/lib/version/vars.sh
. $REDO_ROOT/lib/version/vars
sed -e "s/%VERSION%/$TAG/" -e "s/%DATE%/$DATE/" $2.md
