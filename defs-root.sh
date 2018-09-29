#!/bin/sh -e

# ----------------------------------------------------------------------
# defs-root.sh
# Read definitions at the root of the build tree
# ----------------------------------------------------------------------

# Canonicalize path names
canonicalize()
{
  ( cd $1; pwd )
}

# Canonicalize REDO_ROOT
export REDO_ROOT=`canonicalize $REDO_ROOT`

# Find and source definition files
files=$REDO_ROOT/defs/*.sh
#redo-ifchange $DIR/defs.sh $files
for file in $files
do
  . $file
done 
