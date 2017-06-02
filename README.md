# BioNLP-2016

Here are the scripts, code and vectors for the ACL BioNLP 2016 workshop paper:

Chiu et al. [_How to Train good Word Embeddings for Biomedical NLP_](http://aclweb.org/anthology/W/W16/W16-2922.pdf)

## API Package
word2vec: original word2vec from Mikolov: <https://code.google.com/archive/p/word2vec/>  
wvlib: lib to read word2vec file: <https://github.com/spyysalo/wvlib>  
geniass: lib to segment bioMedical text: <http://www.nactem.ac.uk/y-matsu/geniass/>

## Scripts
pre-process.sh: segment and tokenized input text (e.g. raw PubMed or PMC text) <br />
create_shf_low_text.sh: create lowercased and sentence-shuffled text (input: tokenized text) <br />
createModel.sh: Create word2vec.bin file with different parameters <br />
intrinsicEva.sh: run intrinsic evaluation on UMNSRS and Mayo data-set (input: Dir. for testing vector) <br />
ExtrinsicEva.sh: run extrinsic evaluation <br />

## Code

**Pre-processing**:  
tokenize_text.py: tokenized text (requires NLTK)  
geniass: segment sentence  

**Intrinsic evaluation:**  
evaluate.py: perform intrinisic evaluation

**Extrinsic evaluation**: (Keras folder: Need either tensorflow or theano installed):  
mlp.py: simple feed-forward Neural Network  
setting.py: parameters for the Neual Network  

## Word vectors

<https://drive.google.com/open?id=0BzMCqpcgEJgiUWs0ZnU0NlFTam8>
