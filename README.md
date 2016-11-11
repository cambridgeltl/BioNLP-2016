# BioNLP-2016
Here contain the scripts and code used in ACL-BioNLP 2016 paper: <br />
How to Train good Word Embeddings for Biomedical NLP

## API Package
word2vec: original word2vec from Mikolov (https://code.google.com/archive/p/word2vec/) <br />
wvlib: lib to read word2vec file (https://github.com/spyysalo/wvlib) <br />
geniass: lib to segment bioMedical text (http://www.nactem.ac.uk/y-matsu/geniass/)  <br />

## Scripts
pre-process.sh: segment and tokenized input text (e.g. raw PubMed or PMC text) <br />
create_shf_low_text.sh: create lowercased and sentence-shuffled text (input: tokenized text) <br />
createModel.sh: Create word2vec.bin file with different parameters <br />
intrinsicEva.sh: run intrinsic evaluation on UMNSRS and Mayo data-set (input: Dir. for testing vector) <br />
ExtrinsicEva.sh: run extrinsic evaluation <br />

## Code
Pre-processing: <br />
tokenize_text.py: tokenized text (need NLTK installed) <br />
geniass: segment sentence <br />

Intrinsic evaluation: <br />
evaluate.py: perform intrinisic evaluation <br />

Extrinsic evaluation: (Keras folder: Need either tensorflow or theano installed): <br />
mlp.py: simple feed-forward Neural Network <br />
setting.py: parameters for the Neual Network <br />


https://drive.google.com/open?id=0BzMCqpcgEJgiUWs0ZnU0NlFTam8
