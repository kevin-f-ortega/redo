#!/usr/bin/env python

# ======================================================================
# redo-remove.py
# Implement the redo-remove command
# ======================================================================

import sys, os
import vars_init
vars_init.init(sys.argv[1:])
import vars, state

try:
    targets = sys.argv[1:]
    for t in targets:
        name = os.path.join(
            vars.STARTDIR,
            os.path.join(vars.PWD, t)
        )
        f = state.File(name=name)
        f.is_generated = False
        f.is_override = False
        f.set_checked()
        f.failed_runid = None
        f.zap_deps1()
        f.zap_deps2()
        f.save()
    state.commit()
except KeyboardInterrupt:
    sys.exit(200)
