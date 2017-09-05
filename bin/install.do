# ----------------------------------------------------------------------
# install.do
# Install redo bin files
# ----------------------------------------------------------------------

. ./defs.sh

vars_require_set INSTALL LIBDIR BINDIR

$INSTALL -d $BINDIR

evald $INSTALL -m 0755 $REDO_ROOT/'do' $BINDIR/'do'
for py in $REDO_ROOT/lib/commands/*.py
do
	base=`basename $py .py`
  echo '#!/bin/sh

# ----------------------------------------------------------------------
# '$base'
# ----------------------------------------------------------------------

python '$LIBDIR'/'$base'.py "$@"' > bin.py
	evald $INSTALL -m 0755 bin.py $BINDIR/$base
done
rm -f bin.py
