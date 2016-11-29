# ======================================================================
# targets_seen.py
# Track targets seen for cycle detection
# ======================================================================

import os

def get():
  '''
  Get the list of targets
  '''
  return os.environ['REDO_TARGETS_SEEN'].split()

def add(target):
  '''
  Add a target to the list
  '''
  if target in get():
      return
  os.environ['REDO_TARGETS_SEEN'] += (target + '\n')
