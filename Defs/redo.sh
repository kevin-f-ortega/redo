#!/bin/sh

# ---------------------------------------------------------------------- 
# redo.sh
# Redo targets
# ---------------------------------------------------------------------- 

# Do target in subdirs
subdir_targets()
{
  dofiles=`find . -mindepth 2 -maxdepth 2 -name $2.do`
  for dofile in $dofiles
  do
    echo $dofile | sed 's/\.do$//'
  done | xargs $1
}
