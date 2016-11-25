#!/bin/sh -e

# ----------------------------------------------------------------------
# defs-root.sh
# ----------------------------------------------------------------------

# Canonicalize path names
canonicalize()
{
  here=`pwd`
  cd $1
  pwd
  cd $here
}

export REDO_ROOT=`canonicalize $REDO_ROOT`

files=$REDO_ROOT/Defs/*.sh

redo-ifchange $DIR/defs.sh $files

for file in $files
do
  . $file
done 
