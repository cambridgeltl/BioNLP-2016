#!/bin/bash

set -e
set -u

for d in data/ner/*; do
    echo "Running" `basename $d`
    python conv.py $d
    echo
done
