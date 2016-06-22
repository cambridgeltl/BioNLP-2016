#!/bin/bash

# srun NER datasets.
# Run this script with sbatch.

#SBATCH -A KORHONEN-SL2
#SBATCH -p dtal
#SBATCH --ntasks 21
#SBATCH --time 1200
# dtal nodes don't have infiniband, which causes spurious error
# messages when running with profiling on (default). (info from Stuart)
#SBATCH --profile none

SCRIPT=conv.py
WORDVECS=data/w2v.bin
DATADIR=data/ner/
DATASETS="AnatEM BC2GM BC4CHEMD BC5CDR-chem BioNLP09 BioNLP11EPI BioNLP11ID-ggp BioNLP13CG-chem BioNLP13CG-ggp BioNLP13GE BioNLP13GRO-ggp BioNLP13PC-ggp CRAFT-chem CRAFT-ggp CRAFT-species DNA-meth Ex-PTM linnaeus LION-chem LION-ggp NCBI-disease"

set -e
set -u

for d in $DATASETS; do
    CMD="$SCRIPT $DATADIR/$d $WORDVECS --verbosity 0"
    echo "Executing $CMD"
    srun --exclusive -n 1 bash -c \
"
echo \"--- START $d \$(date) ---\"
$CMD
echo \" --- END $d \$(date) ---\"
" &
done

wait
