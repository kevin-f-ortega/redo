% redo-base(1) Redo %VERSION%
% Avery Pennarun <apenwarr@gmail.com>
% %DATE%

# NAME

redo-base - print the base directory for redo builds

# SYNOPSIS

redo-base


# DESCRIPTION

`redo-base` prints the *base directory*, i.e., the directory
where `redo` dependency information is stored for builds
initiated from the current directory.

The algorithm for finding the base directory is as follows:

- Starting in the current directory, search upwards for
  files named `.redo-base`.

- If any such file is found, then the topmost directory
  containing such a file is the base directory.

- Otherwise the base directory is the home directory.


# REDO

Part of the `redo`(1) suite.


.CREDITS


# SEE ALSO

`redo`(1)
