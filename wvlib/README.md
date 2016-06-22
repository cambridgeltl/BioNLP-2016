wvlib - word vector library
===========================

Work in progress, not currently recommended for any use.

Try the following:

Find 10 words closest to "protein" using word2vec vectors induced on
the text8 demo data

    echo protein | python nearest.py text8.tar.gz -n 10

Find word that has the same relationship to "japan" as "paris" has
to "france"

    echo 'france paris japan' | python analogy.py text8.tar.gz -q -n 1

Evaluate the vectors on the binary classification task using words
from McIntosh and Curran "Reducing semantic drift with bagging and
distributional similarity" (ACL 2009)

    python evalclass.py text8.tar.gz word-classes/McIC-09/*.txt

Evaluate the vectors on the closed-class member retrieval task
using the set of standard amino acids

    python evalset.py text8.tar.gz word-sets/Ohta-bio-sets/standard-amino-acids.txt

The rest of this README is TODO. See scripts for documentation.
