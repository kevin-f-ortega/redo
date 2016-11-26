#!/bin/sh -e

# ----------------------------------------------------------------------
# install.sh
# Install version
# ----------------------------------------------------------------------

. ./defs.sh

sh version.py.sh

evald $INSTALL -d $LIBDIR/version
evald $INSTALL -m 0644 version.py $LIBDIR/version/version.py
evald python -mcompileall $LIBDIR/version
