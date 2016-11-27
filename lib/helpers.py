# ======================================================================
# helpers.py
# Helper functions for redo implementation
# ======================================================================

import os, errno, fcntl

def atoi(v):
    """
    Convert ascii to integer
    """
    try:
        return int(v or 0)
    except ValueError:
        return 0


def join(between, l):
    """
    join between and l
    """
    return between.join(l)


def unlink(f):
    """
    Delete a file at path 'f' if it currently exists.

    Unlike os.unlink(), does not throw an exception if the file didn't already
    exist.
    """
    try:
        os.unlink(f)
    except OSError, e:
        if e.errno == errno.ENOENT:
            pass  # it doesn't exist, that's what you asked for


def close_on_exec(fd, yes):
    """
    Set or clear FD_CLOEXEC for fd
    """
    fl = fcntl.fcntl(fd, fcntl.F_GETFD)
    fl &= ~fcntl.FD_CLOEXEC
    if yes:
        fl |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, fl)


