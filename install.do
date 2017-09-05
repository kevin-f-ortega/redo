#!/bin/sh -e

# ---------------------------------------------------------------------- 
# install.do
# Install redo
# ---------------------------------------------------------------------- 

. ./defs.sh

vars_require_set INSTALL BINDIR

$INSTALL -d $BINDIR
evald $INSTALL -m 0755 'do' $BINDIR/'do'
subdir_targets redo install
