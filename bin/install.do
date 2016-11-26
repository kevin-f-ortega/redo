# ----------------------------------------------------------------------
# install.do
# ----------------------------------------------------------------------

. ./defs.sh

vars_require_set INSTALL LIBDIR BINDIR

$INSTALL -d $BINDIR

for py in $REDO_ROOT/lib/redo*.py
do
	bin=`basename $py .py`
	module=`echo $bin | sed -e 's,-,_,g'`
  echo "#!/usr/bin/python
import sys
sys.path.insert(0, '"$LIBDIR"'))
import $module" > bin.py
	evald $INSTALL -m 0755 bin.py $BINDIR/$bin
done
rm -f bin.py
