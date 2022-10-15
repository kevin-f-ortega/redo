#!/usr/bin/env python3

# ======================================================================
# redo-unlocked.py
# Implement the redo-unlocked command
# ======================================================================

import sys, os
import state
from log import err

if len(sys.argv[1:]) < 2:
    err('%s: at least 2 arguments expected.\n' % sys.argv[0])
    sys.exit(1)

target = sys.argv[1]
deps = sys.argv[2:]

for d in deps:
    assert(d != target)

me = state.File(name=target)

# Build the known dependencies of our primary target.  This *does* require
# grabbing locks.
os.environ['REDO_NO_UNLOCKED'] = '1'
argv = ['redo-ifchange'] + deps
rv = os.spawnvp(os.P_WAIT, argv[0], argv)
if rv:
    sys.exit(rv)

# We know our caller already owns the lock on target, so we don't have to
# acquire another one; tell redo-ifchange about that.  Also, REDO_NO_UNLOCKED
# persists from up above, because we don't want to do UNLOCKED now either.
# (Actually it's most important for the primary target, since it's the one
# who initiated the UNLOCKED in the first place.)
os.environ['REDO_UNLOCKED'] = '1'
argv = ['redo-ifchange', target]
rv = os.spawnvp(os.P_WAIT, argv[0], argv)
if rv:
    sys.exit(rv)
