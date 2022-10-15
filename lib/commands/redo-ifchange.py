#!/usr/bin/env python3

# ======================================================================
# redo-ifchange.py
# Implement the redo-ifchange command
# ======================================================================

import sys, os

import vars_init
vars_init.init(sys.argv[1:])

import vars, state, builder, jobs, deps
from log import debug, debug2, err

def should_build(t):
    f = state.File(name=t)
    if f.is_failed():
        raise builder.ImmediateReturn(32)
    status = deps.isdirty(f, depth = '', max_changed = vars.RUNID)
    if status == [f]:
      return deps.DIRTY
    else:
      # FIXME: This is really confusing!
      # The status can be any one of deps.CLEAN or deps.DIRTY or 
      # a list of targets to build with redo-unlocked.
      return status


rv = 202
try:
    if vars.TARGET and not vars.UNLOCKED:
        me = os.path.join(vars.STARTDIR, 
                          os.path.join(vars.PWD, vars.TARGET))
        f = state.File(name=me)
        debug2('TARGET: %r %r %r\n' % (vars.STARTDIR, vars.PWD, vars.TARGET))
    else:
        f = me = None
        debug2('redo-ifchange: not adding depends.\n')
    try:
        targets = sys.argv[1:]
        if f:
            for t in targets:
                f.add_dep('m', t)
            f.save()
        rv = builder.main(targets, should_build)
    finally:
        jobs.force_return_tokens()
except KeyboardInterrupt:
    sys.exit(200)
state.commit()
sys.exit(rv)
