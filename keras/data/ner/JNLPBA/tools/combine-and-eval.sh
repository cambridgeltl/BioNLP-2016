#!/bin/bash

# Combine given predictions with JNLPBA data and run evaluation.

set -e
set -u 

FILE=$1
TMP=$(mktemp)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JNLPBA_DIR="$SCRIPT_DIR/../original-data/"
GOLD="$JNLPBA_DIR/test/Genia4EReval1.iob2"

python "$SCRIPT_DIR/combine.py" "$GOLD" "$FILE" | \
    python "$SCRIPT_DIR/fixbio.py" - > "$TMP"
"$SCRIPT_DIR/evalIOB2.pl" "$TMP" "$GOLD"

rm -rf $TMP
