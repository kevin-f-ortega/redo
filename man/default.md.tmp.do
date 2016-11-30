#!/bin/sh -e 

# ----------------------------------------------------------------------
# default.md.tmp.do
# ----------------------------------------------------------------------

. ./defs.sh

vars=$REDO_ROOT/version/vars
redo-ifchange $vars $2.md
. $vars
set -f
while read line 
do
  if test "$line" = .CREDITS
  then
    cat credits.txt
  else
    echo $line
  fi
done < $2.md | sed -e "s/%VERSION%/$TAG/" -e "s/%DATE%/$DATE/"
