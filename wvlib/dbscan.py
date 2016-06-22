#!/usr/bin/env python

"""DBSCAN clustering for word vectors.

Requires scikit-learn."""

import sys
import math
import logging

import numpy
import scipy.cluster
import wvlib

import sklearn.cluster
if float(sklearn.__version__) < 0.14:
    # old scikit-learn fails to realize the potential memory usage
    # benefits of the DBSCAN algorithm, making it infeasible for large
    # numbers of vectors (e.g. 40G memory for 100K vectors)
    logging.warning('sklearn < 0.14: DBSCAN calculates whole distance matrix')

from itertools import izip

metrics = [
    'cosine',
    'euclidean',
    # TODO more
]
DEFAULT_METRIC = 'cosine'

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse

    ap=argparse.ArgumentParser()
    ap.add_argument('vectors', nargs=1, metavar='FILE', help='word vectors')
    ap.add_argument('-e', '--eps', default=0.5, type=float,
                    help='max distance between vectors in neighborhood')
    ap.add_argument('-M', '--metric', default=DEFAULT_METRIC, choices=metrics,
                    help='distance metric to apply')
    ap.add_argument('-n', '--normalize', default=False, action='store_true',
                    help='normalize vectors to unit length')
    ap.add_argument('-r', '--max-rank', metavar='INT', default=None, 
                    type=int, help='only consider r most frequent words')
    ap.add_argument('-w', '--whiten', default=False, action='store_true',
                    help='normalize features to unit variance ')
    return ap

def process_options(args):    
    options = argparser().parse_args(args)

    if options.max_rank is not None and options.max_rank < 1:
        raise ValueError('max-rank must be >= 1')
    if options.eps <= 0.0:
        raise ValueError('eps must be > 0')

    wv = wvlib.load(options.vectors[0], max_rank=options.max_rank)

    if options.normalize:
        logging.info('normalize vectors to unit length')
        wv.normalize()

    words, vectors = wv.words(), wv.vectors()

    if options.whiten:
        logging.info('normalize features to unit variance')
        vectors = scipy.cluster.vq.whiten(vectors)

    return words, vectors, options

def write_cluster_ids(words, cluster_ids, out=None):
    """Write given list of words and their corresponding cluster ids to out."""

    assert len(words) == len(cluster_ids), 'word/cluster ids number mismatch'

    if out is None:
        out = sys.stdout
    for word, cid in izip(words, cluster_ids):
        print >> out, '%s\t%d' % (word, cid)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        words, vectors, options = process_options(argv[1:])
    except Exception, e:
        if str(e):
            print >> sys.stderr, 'Error: %s' % str(e)
            return 1
        else:
            raise

    dbscan = sklearn.cluster.DBSCAN(eps=options.eps, metric=options.metric)
    dbscan.fit(numpy.array(vectors))
    noisy = sum(1 for l in dbscan.labels_ if l == -1)
    unique = len(set(dbscan.labels_))
    logging.info('%d clusters, %d noisy, %d vectors' % (unique, noisy,
                                                        len(vectors)))
    if noisy >= len(vectors) / 4:
        logging.warning('%d/%d noisy (-1) labels (try higher eps?)' % \
                            (noisy, len(vectors)))
    elif unique < (len(vectors)/2)**0.5:
        logging.warning('only %d clusters (try lower eps?)' % unique)
    write_cluster_ids(words, dbscan.labels_)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
