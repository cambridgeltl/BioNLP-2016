#!/bin/bash

# Convert word vectors introduced by Collobert and Weston for SENNA
# (http://ronan.collobert.com/senna/) into wvlib format.

# Usage (for bash and SENNA version 3.0):

# First, download senna-v3.0.tgz from
#
#     http://ronan.collobert.com/senna/download.html
#
# and then run
#
#     tar xvzf senna-v3.0.tgz
#     export SENNADIR=`pwd`/senna
#     cd WVLIB-DIR
#     ./tools/convert-senna-embeddings.sh $SENNADIR/hash/words.lst $SENNADIR/embeddings/embeddings.txt
#
# where WVLIB-DIR is the directory where wvlib is installed.
#
# This creates the file cw-senna.tar.gz with Collobert & Weston
# embeddings in wvlib format.

# For information on the derivation of the embeddings, see
# R. Collobert, J. Weston, L. Bottou, M. Karlen, K. Kavukcuoglu and P. Kuksa
# (2011) "Natural Language Processing (Almost) from Scratch", JMLR
# (http://ronan.collobert.com/pub/matos/2011_nlp_jmlr.pdf)

set -e
set -u

if [ $# != 2 ]; then
    echo "Usage: $0 WORDS EMBEDDINGS" 2>&1
    exit 1
fi

words=$1
embeddings=$2
out=cw-senna.tar.gz

word_count=`cat $words | wc -l`
vector_dim=`head -n 1 $embeddings | tr ' ' '\n' | wc -l`

dir=`mktemp -d`

# make config.json
cat > $dir/config.json <<EOF
{
    "version" : 1,
    "word_count" : $word_count,
    "vector_dim" : $vector_dim,
    "format" : "tsv"
}    
EOF

# make vocab, filling in zeros for frequency
perl -pe 's/\s*$/\t0\n/' $words > $dir/vocab.tsv

# make vectors
perl -pe 's/ /\t/g' $embeddings > $dir/vectors.tsv

# convert
python wvlib.py $dir -v npy -o $out

rm -rf $dir
