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
# Whether this process has a token
_has_token = True
# A pair of (read, write) file descriptors for passing tokens between processes
_pipe = None
# A map from file descriptors to pending job completions
_completions = {}

# ----------------------------------------------------------------------
# Private classes
# ----------------------------------------------------------------------

class Completion:
    """
    A job completion
    """
    def __init__(self, name, pid, donefunc):
        # The name of the job
        self.name = name
        # The id of the child process running the job
        self.pid = pid
        # The return value of the child process
        self.rv = None
        # The function to run when the job is done
        self.donefunc = donefunc
        
    def __repr__(self):
        return 'Completion(%s,%d)' % (self.name, self.pid)

# ----------------------------------------------------------------------
# Public functions
# ----------------------------------------------------------------------

def setup(maxjobs):
    """
    Initialize the jobs state
    """
    global _pipe, _toplevel
    if _pipe:
        return  # Already set up
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
        # Start a new server
        _toplevel = maxjobs
        _pipe = _make_pipe(100)
        _put_tokens(maxjobs-1)
        os.putenv('MAKEFLAGS',
                  '%s --jobserver-fds=%d,%d -j' % (os.getenv('MAKEFLAGS'),
                                                    _pipe[0], _pipe[1]))

def put_token():
    """
    Put the token held by this process on the pipe
    """
    global _has_token
    assert(_has_token)
    os.write(_pipe[1], 't')
    _has_token = False


def has_token():
    """
    @return Whether this process has a token
    """
    return _has_token


def get_token(reason):
    """
    Get a token
    @param reason The reason for the token
    """
    global _has_token
    # Ensure the job state is initialized
    setup(1)
    # Loop until we get a token
    while not _has_token:
        _debug('(%r) waiting for token...\n' % reason)
        # Wait for internal or external work to become available
        _wait_internal_or_external()
        if not _has_token:
            # External work
            b = _try_read(_pipe[0], 1)
            if b == None:
                raise Exception('unexpected EOF on token read')
            if b:
                _has_token = True
                _debug('(%r) got a token (%r).\n' % (reason, b))


def running():
    """
    @return Whether this process has pending jobs
    """
    return len(_completions)


def wait_all():
    """
    Wait for all available work
    """
    _debug("wait_all\n")
    while running():
        if _has_token:
            put_token()
        _debug("wait_all: _wait_internal_only()\n")
        # Wait for internal work
        _wait_internal_only()
    _debug("wait_all: empty list\n")
    get_token('self')  # get our token back
    if _toplevel:
        bb = ''
        while 1:
            b = _try_read(_pipe[0], 8192)
            bb += b
            if not b: break
        if len(bb) != _toplevel-1:
            raise Exception('on exit: expected %d tokens; found only %r' 
                            % (_toplevel-1, len(bb)))
        if _pipe:
          os.write(_pipe[1], bb)


def force_return_tokens():
    """
    Force return of tokens for aborted jobs
    """
    n = len(_completions)
    if n:
        _debug('%d tokens left in force_return_tokens\n' % n)
    _debug('returning %d tokens\n' % n)
    for k in _completions.keys():
        del _completions[k]
    if _pipe:
        _put_tokens(n)


def start_job(name, jobfunc, donefunc):
    """
    Start a job
    @param name The name of the job
    @param jobfunc The function representing the job
    @param donefunc The function to call when the job is done
    """
    global _has_token
    get_token(name)
    assert(_has_token)
    _has_token = False
    r,w = _make_pipe(50)
    # Fork a child process to run the job
    pid = os.fork()
    if pid == 0:
        # The child process
        os.close(r)
        rv = 201
        try:
            try:
                # Run the job
                rv = jobfunc() or 0
                _debug('jobfunc completed (%r, %r)\n' % (jobfunc,rv))
            except Exception:
                import traceback
                traceback.print_exc()
        finally:
            _debug('exit: %d\n' % rv)
            os._exit(rv)
    # The main process
    close_on_exec(r, True)
    os.close(w)
    # Put the job completion on _completions
    completion = Completion(name, pid, donefunc)
    _completions[r] = completion


# ----------------------------------------------------------------------
# Private functions
# ----------------------------------------------------------------------

def _wait_internal_or_external():
    """
    Wait for internal or external work to become available.
    Internal work is the completion of a build started by this process.
    External work is a token placed on _pipe[0] by this or another process.
    """
    rfds = _completions.keys()
    if _pipe:
        rfds.append(_pipe[0])
    _wait(rfds)

def _wait_internal_only():
    """
    Wait for internal work only.
    """
    rfds = _completions.keys()
    _wait(rfds)

def _wait(rfds):
    """
    Wait for work to become available.
    @rfds Read file descriptors on which to wait
    """
    assert(rfds)
    r,w,x = select.select(rfds, [], [])
    _debug('_pipe=%r; wfds=%r; readable: %r\n' % (_pipe, _completions, r))
    for fd in r:
        if _pipe and fd == _pipe[0]:
            # External work: handle it in the continuation
            pass
        else:
            # Internal work: handle it here
            completion = _completions[fd]
            _debug("done: %r\n" % completion.name)
            # Get a token
            _put_tokens(1)
            os.close(fd)
            del _completions[fd]
            # Wait for the child job process to finish
            rv = os.waitpid(completion.pid, 0)
            assert(rv[0] == completion.pid)
            _debug("done1: rv=%r\n" % (rv,))
            rv = rv[1]
            if os.WIFEXITED(rv):
                completion.rv = os.WEXITSTATUS(rv)
            else:
                completion.rv = -os.WTERMSIG(rv)
            _debug("done2: rv=%d\n" % completion.rv)
            # Complete the job
            completion.donefunc(completion.name, completion.rv)


def _debug(s):
    if 0:
        sys.stderr.write('jobs#%d: %s' % (os.getpid(),s))
    

def _put_tokens(n):
    """
    If we already have a token, then put n tokens on the pipe.
    If we don't have a token and n > 0, then get a token and put n - 1 tokens on the pipe.
    """
    global _has_token
    _debug('_put_tokens(%d)\n' % n)
    if _has_token:
        num_to_put = n
    elif n > 0:
        _has_token = True
        num_to_put = n-1
    else:
        num_to_put = 0
    if num_to_put > 0:
        os.write(_pipe[1], 't' * num_to_put)


def _timeout(sig, frame):
    pass


def _make_pipe(startfd):
    """
    Make a pipe
    @param startfd The minimum file descriptor number
    @return A pipe (a, b)
    """
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
    # Using djb's suggested way of doing non-blocking reads from a blocking
    # socket: http://cr.yp.to/unix/nonblock.html
    # We can't just make the socket non-blocking, because we want to be
    # compatible with GNU Make, and they can't handle it.
    r,w,x = select.select([fd], [], [], 0)
    if not r:
        return ''  # try again
    # Ok, the socket is readable - but some other process might get there
    # first.  We have to set an alarm() in case our read() gets stuck.
    oldh = signal.signal(signal.SIGALRM, _timeout)
    try:
        signal.alarm(1)  # Emergency fallback
        try:
            b = os.read(_pipe[0], 1)
        except OSError, e:
            if e.errno in (errno.EAGAIN, errno.EINTR):
                # Interrupted or it was nonblocking
                return ''  # Try again
            else:
                raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, oldh)
    return b and b or None  # None means EOF


