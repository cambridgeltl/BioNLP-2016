#!/usr/bin/env python

"""Output pairwise distances between word vectors.

Prints lines with TAB-separated word indices (i, j) and the distance
of the corresponding word vectors under given metric.

Implementation avoids storing the distance matrix in memory, making
application to very large numbers of word vectors feasible.

Distances are assumed to be symmetric, either (i, j) or (j, i) is
included for any (i, j) pair, and self-distances (i, i) are excluded.
Indexing is zero-based by default.

The pairwise distances can be used e.g. as input for clustering tools.
"""

import sys
import logging

import numpy
import wvlib

from scipy.cluster.vq import whiten
from itertools import combinations, izip
from scipy.spatial import distance
# TODO: consider sklearn.neighbors.DistanceMetric if available

# selected distance metrics from scipy
metrics = {
    'cosine' : distance.cosine,
    'euclidean' : distance.euclidean,  
    'minkowski' : distance.minkowski,  
# weighted Minkowski distance omitted, weight vector passing not implemented
    'cityblock' : distance.cityblock,  
    'seuclidean' : distance.seuclidean, 
    'sqeuclidean' : distance.sqeuclidean,
    'correlation' : distance.correlation,
    'chebyshev' : distance.chebyshev,  
    'canberra' : distance.canberra,   
    'braycurtis' :  distance.braycurtis, 
    'mahalanobis' : distance.mahalanobis,
# boolean vector distance metrics omitted, word vectors assumed continuous
# (hamming, jaccard, yule, matching, dice, kulsinski, rogerstanimoto,
# russellrao, sokalmichener, sokalsneath)
}
DEFAULT_METRIC='cosine'

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse

    ap=argparse.ArgumentParser()
    ap.add_argument('vectors', nargs=1, metavar='FILE', help='word vectors')
    ap.add_argument('-a', '--approximate', default=False, action='store_true',
                    help='filter by approximate similarity (with -t)')
    ap.add_argument('-i', '--min-index', default=0, type=int,
                    help='index of first word (default 0)')
    ap.add_argument('-M', '--metric', default=DEFAULT_METRIC, 
                    choices=sorted(metrics.keys()),
                    help='distance metric to apply')
    ap.add_argument('-n', '--normalize', default=False, action='store_true',
                    help='normalize vectors to unit length')
    ap.add_argument('-r', '--max-rank', metavar='INT', default=None, 
                    type=int, help='only consider r most frequent words')
    ap.add_argument('-t', '--threshold', metavar='FLOAT', default=None,
                    type=float, help='only output distances <= t')
    ap.add_argument('-T', '--tolerance', metavar='FLOAT', default=0.1,
                    type=float, help='approximation tolerace (with -a)')
    ap.add_argument('-w', '--whiten', default=False, action='store_true',
                    help='normalize features to unit variance ')
    ap.add_argument('-W', '--words',  default=False, action='store_true',
                    help='output words instead of indices')
    return ap

def process_options(args):    
    options = argparser().parse_args(args)

    if options.max_rank is not None and options.max_rank < 1:
        raise ValueError('max-rank must be >= 1')
    if options.threshold is not None and options.threshold < 0.0:
        raise ValueError('threshold must be >= 0')
    if options.tolerance is not None and options.tolerance < 0.0:
        raise ValueError('tolerance must be >= 0')
    if options.approximate and not options.threshold:
        raise ValueError('approximate only makes sense with a threshold')
    if options.approximate and options.metric != 'cosine':
        raise NotImplementedError('approximate only supported for cosine')

    wv = wvlib.load(options.vectors[0], max_rank=options.max_rank)

    if options.normalize:
        logging.info('normalize vectors to unit length')
        wv.normalize()

    words, vectors = wv.words(), wv.vectors()

    if options.whiten:
        # whitening should be implemented in wvlib to support together with
        # approximate similarity
        if options.approximate:
            raise NotImplemenedError
        logging.info('normalize features to unit variance')
        vectors = whiten(vectors)

    return words, vectors, wv, options

def make_dist(vectors, options):
    if options.metric != 'cosine':
        return vectors, metrics[options.metric]
    else:
        # normalize once only
        vectors = [v/numpy.linalg.norm(v) for v in vectors]
        return vectors, lambda u, v: 1 - numpy.dot(u, v)

def make_filters(options):
    strict = approx = lambda _: False
    if options.threshold is not None:
        strict = lambda d: d > options.threshold
        if options.approximate:
            approx = lambda d: d > options.threshold + options.tolerance
    return strict, approx

def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        words, vectors, wv, options = process_options(argv[1:])
    except Exception, e:
        if str(e):
            print >> sys.stderr, 'Error: %s' % str(e)
            return 1
        else:
            raise

    m = options.min_index
    vectors, dist = make_dist(vectors, options)
    strict_filter, approx_filter = make_filters(options)
    approx = options.threshold is not None
    hash_bits = 1000

    def index_str(i):
        if not options.words:
            return str(i)
        else:
            return words[i-m]            

    approx_count = exact_count = total_count = 0
    for i_j, v_u in izip(combinations(xrange(m, m+len(vectors)), 2),
                         combinations(vectors, 2)):
        total_count += 1
        if options.approximate:
            w1, w2 = words[i_j[0]-m], words[i_j[1]-m]
            approx_count += 1
            if approx_filter(1 - wv.approximate_similarity(w1, w2, hash_bits)):
                continue
        exact_count += 1
        d = dist(v_u[0], v_u[1])
        if strict_filter(d):
            continue
        print '%s\t%s\t%f' % (index_str(i_j[0]), index_str(i_j[1]), d)

    logging.info('%d approx, %d exact, %d total' % (approx_count, exact_count,
                                                    total_count))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    # runs main() with profiling. To see a profile, run e.g.
    #    python -c 'import pstats; pstats.Stats("profile").strip_dirs().sort_stats("time").print_stats()' | less
#    import cProfile
#    cProfile.run('main(sys.argv)', 'profile')
