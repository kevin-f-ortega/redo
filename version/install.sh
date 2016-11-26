#!/bin/sh -e

# ----------------------------------------------------------------------
# install.sh
# Install version
# ----------------------------------------------------------------------

. ./defs.sh

redo-ifchange version.py

evald $INSTALL -d $LIBDIR/version
evald $INSTALL -m 0644 version.py $LIBDIR/version.py
