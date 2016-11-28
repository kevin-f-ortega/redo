# ======================================================================
# deps.py
# Compute dependences
# ======================================================================

import sys, os
import vars, state, builder
from log import debug

# ----------------------------------------------------------------------
# Public constants
# ----------------------------------------------------------------------

CLEAN = 0
DIRTY = 1

# ----------------------------------------------------------------------
# Public functions
# ----------------------------------------------------------------------

def isdirty(
    f,
    depth, 
    max_changed,
    is_checked=state.File.is_checked,
    set_checked=state.File.set_checked_save
):
    '''
    Determine whether a file needs to be built
    @param f The file name
    @param depth The recursion depth
    @param max_changed The maximum changed run ID
    @param The function for determining whether f is checked
    @param The function for setting that the file is checked and saving state
    @return One of the following: CLEAN (the file is clean); or
            DIRTY (the file is dirty); or a list of targets to build
    '''
    if vars.DEBUG >= 1:
        debug('%s?%s\n' % (depth, f.nicename()))

    if f.failed_runid:
        debug('%s-- DIRTY (failed last time)\n' % depth)
        return DIRTY
    if f.changed_runid == None:
        debug('%s-- DIRTY (never built)\n' % depth)
        return DIRTY
    if f.changed_runid > max_changed:
        debug('%s-- DIRTY (built)\n' % depth)
        return DIRTY  # has been built more recently than parent
    if is_checked(f):
        if vars.DEBUG >= 1:
            debug('%s-- CLEAN (checked)\n' % depth)
        return CLEAN  # has already been checked during this session
    if not f.stamp:
        debug('%s-- DIRTY (no stamp)\n' % depth)
        return DIRTY

    newstamp = f.read_stamp()
    if f.stamp != newstamp:
        if newstamp == state.STAMP_MISSING:
            debug('%s-- DIRTY (missing)\n' % depth)
        else:
            debug('%s-- DIRTY (mtime)\n' % depth)
        if f.csum:
            return [f]
        else:
            return DIRTY

    targets = []
    for mode,f2 in f.deps():
        status = CLEAN
        if mode == 'c' and os.path.exists(os.path.join(vars.BASE, f2.name)):
            debug('%s-- DIRTY (created)\n' % depth)
            status = DIRTY
        elif mode == 'm':
            sub = isdirty(f2, depth = depth + '  ',
                          max_changed = max(f.changed_runid,
                                            f.checked_runid),
                          is_checked=is_checked, set_checked=set_checked)
            if sub:
                debug('%s-- DIRTY (sub)\n' % depth)
                status = sub
        else:
            assert(mode in ('c','m'))
        if f.csum:
            # f is "checksummable": dirty f2 means f needs to redo,
            # but f might turn out to be clean after that (ie. our parent
            # might not be dirty).
            if status == DIRTY:
                # f2 is definitely dirty, so f definitely needs to
                # redo.  However, after that, f might turn out to be
                # unchanged.
                return [f]
            elif isinstance(status, list):
                # our child f2 might be dirty, but it's not sure yet.  It's
                # given us a list of targets we have to redo in order to
                # be sure.
                targets += status
        elif not status == CLEAN:
            # f is a "normal" target: dirty f2 means f is instantly dirty
            return status

    if targets:
        # f is *maybe* dirty because at least one of its children is maybe
        # dirty.  targets has accumulated a list of "topmost" uncertain
        # objects in the tree.  If we build all those, we can then
        # redo-ifchange f and it won't have any uncertainty next time.
        return targets

    # if we get here, it's because the target is clean
    if f.is_override:
        state.warn_override(f.name)
    set_checked(f)
    return CLEAN


