#!/bin/sh
#
# generate.sh -- (c)2020 Henrique Moreira


LANGS="en pt_PT"


usage ()
{
 echo "$0 [COMMAND] [options]

Commands are:
   start	Generate dicts.
"
 exit 0
}


do_start ()
{
 local RES=0
 local PT
 local TWO
 local RAW
 local NICKS=$LANGS

 [ "$*" ] && NICKS="$*"
 [ "$NICKS" = "" ] && return 2

 if [ ! -d dictraw ]; then
	echo "No dictraw/ directory here: $(pwd)"
	return 2
 fi
 for PT in $NICKS; do
	[ "$PT" = "" ] && continue
	TWO=$(echo $PT | sed 's/^\(..\).*/\1/')
	echo -n "Generating dicts for $PT (${TWO}) "
	RAW=dictraw/words-${TWO}.lst
	if [ ! -f $RAW ]; then
		aspell -d $PT dump master > $RAW
		RES=$?
		if [ $RES != 0 ]; then
			echo "-- failed!"
			rm -f $RAW
			show_installed_aspell $*
			return 1
		fi
	else
		echo -n "Skipped (${PT})"
	fi
	echo .
	cat $RAW | grep ^'[A-Za-z][a-z]' | grep -v "'" | \
		sort > dictraw/strict-${TWO}.lst
	cat dictraw/strict-${TWO}.lst | grep ^'[A-Za-z][a-z][a-z]'$ | \
		sort | uniq > dictraw/strict-${TWO}.w3.lst
	cat dictraw/strict-${TWO}.lst | grep ^'[A-Za-z][a-z][a-z][a-z]'$ | \
		sort | uniq > dictraw/strict-${TWO}.w4.lst
 done
 return $RES
}


show_installed_aspell ()
{
 local LANG
 local LST
 local NICKS="$LANGS"

 [ "$*" ] && NICKS="$*"
 [ "$NICKS" = "" ] && return 2

 LST=$(rpm -qa | grep -v '\-devel\-' | grep aspell-'[a-z][A-Za-z]')
 echo "List: $(echo $LST)"; echo ...
 for LANG in $NICKS ; do
	rpm -qa | grep -v '\-devel\-' | grep aspell-"$LANG"-
	if [ $? != 0 ]; then
		echo "Could not find: $LANG"
		return 1
	fi
	echo "LANG: $LANG ok
"
 done
 echo "Checked language nicks: $NICKS"
 return 0
}


#
# Main script
#
case $1 in
	-h|--help)
		usage
		;;
	start)
		shift
		cd $(dirname $0)
		[ $? != 0 ] && exit 4
		do_start $*
		RES=$?
		;;
	show)
		shift
		show_installed_aspell $*
		RES=$?
		;;
	*)
		usage
		;;
esac

# Exit status
exit $RES

