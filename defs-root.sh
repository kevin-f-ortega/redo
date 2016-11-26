#!/bin/sh -e

# ----------------------------------------------------------------------
# defs-root.sh
# ----------------------------------------------------------------------

# Canonicalize path names
canonicalize()
{
  ( cd $1; pwd )
}

export REDO_ROOT=`canonicalize $REDO_ROOT`

files=$REDO_ROOT/Defs/*.sh

redo-ifchange $DIR/defs.sh $files

for file in $files
do
  . $file
done 
