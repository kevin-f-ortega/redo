% redo-remove(1) Redo %VERSION%
% Rob Bocchino (*bocchino@icloud.com*)
% %DATE%

# NAME

redo-remove - remove dependency information

# SYNOPSIS

redo-remove [targets...]


# DESCRIPTION

`redo-remove` removes all dependency information for each
of its targets.
This is useful, for example, if you generate a file `foo`
with a do file `foo.do`, but later decide that you want
to maintain `foo` by hand.
In this case, `redo` remembers that `foo` is a generated file,
so from then on it will print a warning message whenever
you run `redo-ifchange foo` (as you might want to do, if
some other file depends on the handwritten version of `foo`).
Running `redo-remove foo` makes this warning message go away.


# REDO

Part of the `redo`(1) suite.


.CREDITS


# SEE ALSO

`redo`(1)
