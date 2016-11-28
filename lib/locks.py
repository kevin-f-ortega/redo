# ======================================================================
# locks.py
# Track held locks for cycle detection
# ======================================================================

import os

def get():
  '''
  Get the list of held locks
  '''
  return os.environ['REDO_LOCKS'].split(':')

def add(name):
  '''
  Add a lock to the list of held locks
  '''
  if name in get():
      return
  locks = os.environ['REDO_LOCKS']
  if len(locks) > 0:
      os.environ['REDO_LOCKS'] = locks + ':' + name
  else:
      os.environ['REDO_LOCKS'] = name
