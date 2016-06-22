#!/bin/sh

if [ $# -ne 2 ] && [ $# -ne 3 ]; then
	echo "Usage: run_geniass.sh <in-file> <out-file> [path-to-ruby]" 1>&2
	exit 1
fi

PROG_DIR=`dirname $0`

IN_FILE=$1
OUT_FILE=$2
RUBY=$3

if [ `echo $IN_FILE | grep -c "^/"` -eq 0 ]; then IN_FILE=$PWD/$IN_FILE; fi
if [ `echo $OUT_FILE | grep -c "^/"` -eq 0 ]; then OUT_FILE=$PWD/$OUT_FILE; fi

cd $PROG_DIR && ./geniass $IN_FILE $OUT_FILE $RUBY
