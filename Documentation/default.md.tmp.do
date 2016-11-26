#!/bin/sh -e 

# ----------------------------------------------------------------------
# default.md.tmp.do
# ----------------------------------------------------------------------

. ./defs.sh

vars=$REDO_ROOT/version/vars
redo-ifchange $vars $2.md
. $vars
sed -e "s/%VERSION%/$TAG/" -e "s/%DATE%/$DATE/" $2.md
