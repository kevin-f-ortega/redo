# ======================================================================
# helpers.py
# Helper functions for redo implementation
# ======================================================================

import os, errno, fcntl, shutil

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


def rename(src, dest):
    """
    Unconditionally rename a file or directory, even if it clobbers
    an existing one
    """
    if os.path.isdir(dest):
        remove(dest)
    os.rename(src, dest)
    

def remove(path):
    """
    Unconditionally remove a path name, whether file or directory
    """
    if os.path.isfile(path):
        os.unlink(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
      

def close_on_exec(fd, yes):
    """
    Set or clear FD_CLOEXEC for fd
    """
    fl = fcntl.fcntl(fd, fcntl.F_GETFD)
    fl &= ~fcntl.FD_CLOEXEC
    if yes:
        fl |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, fl)


