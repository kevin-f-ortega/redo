#!/bin/sh -e

# ----------------------------------------------------------------------
# all.do
# ----------------------------------------------------------------------

. ./defs.sh

subdir_targets redo-ifchange all
(cd man; ./warn) >&2
