#!/bin/sh

# ---------------------------------------------------------------------- 
# general.sh
# general definitions
# ---------------------------------------------------------------------- 

# Eval; print command to stderr if in debug mode
evald()
{
  if test -n "$DEBUG"
  then
    echoerr "$@"
  fi
  $@
}

# Echo args to stderr
echoerr()
{
  echo $@ 1>&2
}

# Do command on all patterns
doall()
{
  if test $# -eq 0
  then
    echoerr 'usage: doall command patterns...'
    exit 1
  fi
  cmd=$1
  shift
  for arg in $@
  do
    for file in `find . -maxdepth 1 -name "$arg"`
    do
      evald "$cmd $file"
    done
  done
}

# Remove temporary files
rm_tmp()
{
  evald doall rm '*~' '.*~'
}
