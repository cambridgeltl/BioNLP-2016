#!/bin/bash

set -u
set -e

VEC=${1:-text8.tar.gz}
DIR=${2:-word-similarities/}

echo "Evaluating $VEC on word rankings in $DIR" >&2

python evalrank.py $VEC `find "$DIR" -name '*.txt'`
