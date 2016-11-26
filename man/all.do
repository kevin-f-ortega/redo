#!/bin/sh -e

# ----------------------------------------------------------------------
# all.do
# ----------------------------------------------------------------------

. ./defs.sh

/bin/ls *.md | sed 's/\.md/.1/' | xargs redo-ifchange
subdir_targets redo-ifchange all
