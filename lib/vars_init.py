# ======================================================================
# vars_init.py
# Initialize environment variables
# ======================================================================

import sys, os

def init(targets):
    if not os.environ.get('REDO'):
        # toplevel call to redo
        if len(targets) == 0:
            targets.append('all')
        exenames = [os.path.abspath(sys.argv[0]),
                    os.path.realpath(sys.argv[0])]
        dirnames = [os.path.dirname(p) for p in exenames]
        trynames = ([os.path.abspath(p+'/../lib/redo') for p in dirnames] +
                    [p+'/redo-sh' for p in dirnames] +
                    dirnames)
        seen = {}
        dirs = []
        for k in trynames:
            if not seen.get(k):
                seen[k] = 1
                dirs.append(k)
        os.environ['PATH'] = ':'.join(dirs) + ':' + os.environ['PATH']
        os.environ['REDO'] = os.path.abspath(sys.argv[0])

    if not os.environ.get('REDO_BASE'):
        base = os.path.expanduser('~')
        atoms = os.getcwd().split('/')
        for i in range(len(atoms), 0, -1):
            possible_base = '/'.join(atoms[:i])
            if os.path.exists(possible_base + '/.redo-base'):
                base = possible_base
        os.environ['REDO_BASE'] = base
        os.environ['REDO_STARTDIR'] = os.getcwd()

        import state
        state.init()

    os.environ['REDO_TARGETS_SEEN'] = os.environ.get('REDO_TARGETS_SEEN', '')
