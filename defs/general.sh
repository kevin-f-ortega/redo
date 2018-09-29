#!/bin/sh

# ---------------------------------------------------------------------- 
# general.sh
# General definitions
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

# Do command in all subdirectories
subdir_commands()
{
  commands=`find . -mindepth 2 -maxdepth 2 -name $1`
  shift
  for command in $commands
  do
    dir=`dirname $command`
    base=`basename $command`
    (cd $dir; evald ./$base "$@")
  done
}

# Remove temporary files
rm_tmp()
{
  doall 'rm -R' '*~' '.*~' '*.tmp' '.do_built*'
}
