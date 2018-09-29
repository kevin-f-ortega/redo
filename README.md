# The redo Build System
*This repository is based on code and documentation licensed from Avery Pennarun.
Original contributions are copyright (C) 2016 by Rob Bocchino.*

This repository is a fork of 
[Avery Pennarun's implementation of `redo`](https://github.com/apenwarr/redo) 
("apenwarr `redo`").
`redo` is a suite of simple but powerful tools that let you write build
rules as shell scripts (called "`.do` files") with dynamic dependency tracking.
For more information about apenwarr `redo`, see
[this README file](https://github.com/apenwarr/redo/blob/master/README.md).

## Goals

My goals for this repository are as follows:

1. To be backwards compatible with, and provide a drop-in replacement for, 
apenwarr `redo`.

2. As development on apenwarr `redo` seems to have stopped, to continue
   development, including code refactoring, enhancements, and bug fixes.

## Contributions

To date, I have made the following improvements to apenwarr `redo`:

* Improved the installation procedure.

* Fixed the problem of [multiple inconsistent .redo directories](https://github.com/bocchino/redo/issues/1).

* Improved the behavior when running a `.do` script would 
[clobber an existing directory](https://github.com/bocchino/redo/commit/434da58fd675189d37e81dafb52de1228bba605e).

* Improved the error reporting when a 
[remove or rename operation fails](https://github.com/bocchino/redo/commit/7fd7727aacf4aba26877a1de133a9f4dd44e2e6e)
(e.g., when attempting to create a target in a directory that doesn't exist).

* Added cycle detection, so that `redo` prints an error message and halts
  instead of hanging when it encounters a cyclic build dependence.

* Added a command `redo-remove` for removing dependency information
  about a file. This is useful, for example, if a file gets marked as generated
  but you later decide you want to maintain it by hand.

* Fixed bugs that caused 
  [spurious warnings about updated files](https://github.com/bocchino/redo/commit/5c2c7fb8b81207e06e03ea3dfb83237bbd7f4352) on 
  some systems.

* Removed the deprecated 
  ["old-args" feature](https://github.com/bocchino/redo/commit/cba16d93f19d21527872e7379ba18462f29d8944).

* Refactored the code.

## Contents

This repository contains the following items:

* `bash_completion.d`: `bash` completion rules for `redo`.

* `bin`: Rules for generating the "binary files" of the `redo` tool suite
(really, they are executable python files).

* `defs`: Definitions used by the build system in this repository, 
including system-specific configuration.

* `do`: A minimal implementation of `redo`, written in shell, 
that builds everything without tracking any dependencies. 
It is useful for running `.do` files on systems where `redo`
is not available.
In particular, you run `do` on the build system in this repository
to build everything before installing `redo` (see below).

* `lib`: The "library files" for the `redo` tool suite (they are python files).

* `man`: Man pages for the `redo` tool suite.

* `shell`: Rules for finding a good shell for running `.do` files.

* `tests`: Tests for the `redo` tools.

* `version`: Rules for computing the `redo` version from information provided by `git`.

## Requirements

To use this software, you need the following:

1. A Unix environment.

2. A working python 2 installation.

3. A shell capable of running the `.do` files in this repository (e.g., `bash`).
Any modern Unix system should have such a shell, and the installation procedure
should find it (see below).

## Installation

To install the software, carry out the following steps:

1. Clone this repository to your computer.

2. Copy `defs/config.sh.example` to `defs/config.sh`.
Edit the file so the following variables have the desired values:

  * `INSTALL`: The command to use for installation.

  * `MANDIR`: The directory for installing man pages.

  * `BINDIR`: The directory for installing the "binary files" for the
`redo` tools.

  * `LIBDIR`: The directory for installing the library files for the
`redo` tools.

  If you don't change anything, the installation will go into subdirectories
  of `$REDO_ROOT/installdir`, where `REDO_ROOT` is the top-level directory
  of this repository.
  To install `redo` globally, change `$REDO_ROOT/installdir` 
  to something like `/usr`.

3. In the top-level directory of this repository, run `./do all`.
This step should build everything without errors.
If there are any errors, fix them.

4. In the top-level directory of this repository, run `./install`.
Note that if you opted for a global installation in step 2, you may
have to run `sudo ./install`.

5. If the directory that you picked for `$BINDIR` in step 2 is not already in your 
Unix `PATH`, then add it now.
It's best to do this in the startup configuration file for your shell
(e.g., `.bashrc`).

6. Check that you have a good `redo` installation: `which redo`.

Once you have a working installation, you should be able to run `redo` on
any of the `.do` files in this repository. For example:

    redo clean # To clean everything
    redo all # To build everything
    redo tests/test # To run all the tests in the tests directory
