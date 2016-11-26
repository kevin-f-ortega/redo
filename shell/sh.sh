#!/bin/sh -e

# ----------------------------------------------------------------------
# sh.do
# Find a good shell to support redo
# ----------------------------------------------------------------------

. ./defs.sh

exec >&2

mkdir -p tmp

GOOD=
WARN=

# Note: list low-functionality, maximally POSIX-like shells before more
# powerful ones.  We want weaker shells to take precedence, as long as they
# pass the tests, because weaker shells are more likely to point out when you
# use some non-portable feature.
for sh in dash sh /usr/xpg4/bin/sh ash posh mksh ksh ksh88 ksh93 pdksh \
		bash zsh busybox; do
	printf "%-30s" "Testing $sh..."
	FOUND=`which $sh 2>/dev/null` || { echo "missing"; continue; }
	
	# It's important for the file to actually be named 'sh'.  Some
	# shells (like bash and zsh) only go into POSIX-compatible mode if
	# they have that name.  If they're not in POSIX-compatible mode,
	# they'll fail the test.
	rm -f tmp/sh
	ln -s $FOUND tmp/sh
	
	set +e
	( cd $REDO_ROOT/t && $REDO_ROOT/shell/tmp/sh shelltest.od >shelltest.tmp 2>&1 )
	RV=$?
	set -e
	
	msgs=
	crash=
	while read line; do
		#echo "line: '$line'" >&2
		stripw=${line#warning: }
		stripf=${line#failed: }
		crash=$line
		[ "$line" = "$stripw" ] || msgs="$msgs W$stripw"
		[ "$line" = "$stripf" ] || msgs="$msgs F$stripf"
	done <$REDO_ROOT/t/shelltest.tmp
	rm -f $REDO_ROOT/t/shelltest.tmp
	msgs=${msgs# }
	crash=${crash##*:}
	crash=${crash# }
	
	case $RV in
		40) echo "ok $msgs"; [ -n "$GOOD" ] || GOOD=$FOUND ;;
		41) echo "failed    $msgs" ;;
		42) echo "warnings  $msgs"; [ -n "$WARN" ] || WARN=$FOUND ;;
		*)  echo "crash     $crash" ;;
	esac
done

rm -rf tmp

if [ -n "$GOOD" ]; then
	echo "Selected perfect shell: $GOOD"
	ln -fs $GOOD sh
elif [ -n "$WARN" ]; then
	echo "Selected mostly good shell: $WARN"
	ln -fs $WARN sh
else
	echo "No good shells found!  Maybe install dash, bash, or zsh."
	exit 13
fi
