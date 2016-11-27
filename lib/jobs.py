# ====================================================================== 
# jobs.py
# Manage redo jobs
# ====================================================================== 

import sys, os, errno, select, fcntl, signal
from helpers import atoi, close_on_exec

# ----------------------------------------------------------------------
# Private variables
# ----------------------------------------------------------------------

# The maximum number of running jobs across all processes
_toplevel = 0
# The number of tokens held by the current process
_mytokens = 1
# A pair of (read, write) file descriptors for passing tokens between processes
_pipe = None
# The queue of jobs created by this process and waiting to run
_waitfds = {}

# ----------------------------------------------------------------------
# Private classes
# ----------------------------------------------------------------------

class Job:
    """
    A waiting job
    """
    def __init__(self, name, pid, donefunc):
        self.name = name
        self.pid = pid
        self.rv = None
        self.donefunc = donefunc
        
    def __repr__(self):
        return 'Job(%s,%d)' % (self.name, self.pid)

# ----------------------------------------------------------------------
# Public functions
# ----------------------------------------------------------------------

def setup(maxjobs):
    """
    Initialize the jobs state
    """
    global _pipe, _toplevel
    if _pipe:
        return  # already set up
    _debug('setup(%d)\n' % maxjobs)
    flags = ' ' + os.getenv('MAKEFLAGS', '') + ' '
    FIND = ' --jobserver-fds='
    ofs = flags.find(FIND)
    if ofs >= 0:
        s = flags[ofs+len(FIND):]
        (arg,junk) = s.split(' ', 1)
        (a,b) = arg.split(',', 1)
        a = atoi(a)
        b = atoi(b)
        if a <= 0 or b <= 0:
            raise ValueError('invalid --jobserver-fds: %r' % arg)
        try:
            fcntl.fcntl(a, fcntl.F_GETFL)
            fcntl.fcntl(b, fcntl.F_GETFL)
        except IOError, e:
            if e.errno == errno.EBADF:
                raise ValueError('broken --jobserver-fds from make; prefix your Makefile rule with a "+"')
            else:
                raise
        _pipe = (a,b)
    if maxjobs and not _pipe:
        # need to start a new server
        _toplevel = maxjobs
        _pipe = _make_pipe(100)
        _release(maxjobs-1)
        os.putenv('MAKEFLAGS',
                  '%s --jobserver-fds=%d,%d -j' % (os.getenv('MAKEFLAGS'),
                                                    _pipe[0], _pipe[1]))

def put_token():
    """
    Put one token held by this process on the pipe
    """
    global _mytokens
    assert(_mytokens == 1)
    os.write(_pipe[1], 't')
    _mytokens = 0


def has_token():
    """
    @return Whether this process has a token
    """
    _assert_mytokens_valid()
    if _mytokens == 1:
        return True


def get_token(reason):
    """
    Get a token
    @param reason The reason for the token
    """
    global _mytokens
    # Ensure the job state is initialized
    setup(1)
    while 1:
        _assert_mytokens_valid()
        if _mytokens == 1:
            # We already have a token
            _debug("_mytokens is %d\n" % _mytokens)
            assert(_mytokens == 1)
            _debug('(%r) used my own token...\n' % reason)
            break
        _debug('(%r) waiting for tokens...\n' % reason)
        # Wait for internal or external work to become available
        wait(external=1)
        _assert_mytokens_valid()
        if _mytokens == 1:
            # Internal work
            break
        else:
            # External work
            b = _try_read(_pipe[0], 1)
            if b == None:
                raise Exception('unexpected EOF on token read')
            if b:
                _mytokens += 1
                _debug('(%r) got a token (%r).\n' % (reason, b))
                break
    _assert_mytokens_valid()


def running():
    """
    @return Whether this process has pending work
    """
    return len(_waitfds)


def wait_all():
    _debug("wait_all\n")
    while running():
        while _mytokens >= 1:
            put_token()
        _debug("wait_all: wait()\n")
        # Wait for internal work
        wait(external=0)
    _debug("wait_all: empty list\n")
    get_token('self')  # get my token back
    if _toplevel:
        bb = ''
        while 1:
            b = _try_read(_pipe[0], 8192)
            bb += b
            if not b: break
        if len(bb) != _toplevel-1:
            raise Exception('on exit: expected %d tokens; found only %r' 
                            % (_toplevel-1, len(bb)))
        os.write(_pipe[1], bb)


def force_return_tokens():
    n = len(_waitfds)
    if n:
        _debug('%d tokens left in force_return_tokens\n' % n)
    _debug('returning %d tokens\n' % n)
    for k in _waitfds.keys():
        del _waitfds[k]
    if _pipe:
        _release(n)


def start_job(reason, jobfunc, donefunc):
    global _mytokens
    _assert_mytokens_valid()
    get_token(reason)
    assert(_mytokens == 1)
    _mytokens = 0
    r,w = _make_pipe(50)
    pid = os.fork()
    if pid == 0:
        # child
        os.close(r)
        rv = 201
        try:
            try:
                rv = jobfunc() or 0
                _debug('jobfunc completed (%r, %r)\n' % (jobfunc,rv))
            except Exception:
                import traceback
                traceback.print_exc()
        finally:
            _debug('exit: %d\n' % rv)
            os._exit(rv)
    close_on_exec(r, True)
    os.close(w)
    pd = Job(reason, pid, donefunc)
    _waitfds[r] = pd


# ----------------------------------------------------------------------
# Private functions
# ----------------------------------------------------------------------

def wait(external):
    """
    Wait for work to become available.
    There are two kinds of work: internal and external.
    Internal work is a job that completes a build that this process started.
    External work is a token released by another process on _pipe[0].
    @param external Whether we want external work
    """
    rfds = _waitfds.keys()
    if _pipe and external:
        rfds.append(_pipe[0])
    assert(rfds)
    r,w,x = select.select(rfds, [], [])
    _debug('_pipe=%r; wfds=%r; readable: %r\n' % (_pipe, _waitfds, r))
    for fd in r:
        if _pipe and fd == _pipe[0]:
            # External work: handle it in the continuation
            pass
        else:
            # Internal work: handle it here
            pd = _waitfds[fd]
            _debug("done: %r\n" % pd.name)
            # Get a token
            _release(1)
            os.close(fd)
            del _waitfds[fd]
            rv = os.waitpid(pd.pid, 0)
            assert(rv[0] == pd.pid)
            _debug("done1: rv=%r\n" % (rv,))
            rv = rv[1]
            if os.WIFEXITED(rv):
                pd.rv = os.WEXITSTATUS(rv)
            else:
                pd.rv = -os.WTERMSIG(rv)
            _debug("done2: rv=%d\n" % pd.rv)
            # Finish the job
            pd.donefunc(pd.name, pd.rv)


def _debug(s):
    if 0:
        sys.stderr.write('jobs#%d: %s' % (os.getpid(),s))
    

def _release(n):
    global _mytokens
    _debug('release(%d)\n' % n)
    _mytokens += n
    if _mytokens > 1:
        os.write(_pipe[1], 't' * (_mytokens-1))
        _mytokens = 1


def _timeout(sig, frame):
    pass


def _make_pipe(startfd):
    (a,b) = os.pipe()
    fds = (fcntl.fcntl(a, fcntl.F_DUPFD, startfd),
            fcntl.fcntl(b, fcntl.F_DUPFD, startfd+1))
    os.close(a)
    os.close(b)
    return fds


def _try_read(fd, n):
    """
    Read n bytes from fd
    """
    # using djb's suggested way of doing non-blocking reads from a blocking
    # socket: http://cr.yp.to/unix/nonblock.html
    # We can't just make the socket non-blocking, because we want to be
    # compatible with GNU Make, and they can't handle it.
    r,w,x = select.select([fd], [], [], 0)
    if not r:
        return ''  # try again
    # ok, the socket is readable - but some other process might get there
    # first.  We have to set an alarm() in case our read() gets stuck.
    oldh = signal.signal(signal.SIGALRM, _timeout)
    try:
        signal.alarm(1)  # emergency fallback
        try:
            b = os.read(_pipe[0], 1)
        except OSError, e:
            if e.errno in (errno.EAGAIN, errno.EINTR):
                # interrupted or it was nonblocking
                return ''  # try again
            else:
                raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, oldh)
    return b and b or None  # None means EOF


def _pre_job(r, w, pfn):
    os.close(r)
    if pfn:
        pfn()

def _assert_mytokens_valid():
    assert _mytokens >= 0 and _mytokens <= 1, "_mytokens=%d\n" % _mytokens

