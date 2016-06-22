#!/usr/bin/env python

"""Given phrases p1 and p2, find nearest neighbors to both and rank
pairs of neighbors by similarity to vec(p2)-vec(p1) in given word
representation.

The basic idea is a straightforward combination of nearest neighbors
and analogy as in word2vec (https://code.google.com/p/word2vec/).
"""

import sys
import os

import numpy

import wvlib

from common import process_args, query_loop

def process_query(wv, query, options=None):
    vectors = [wv.words_to_vector(q) for q in query]
    words = [w for q in query for w in q]
    nncount = 100 # TODO: add CLI parameter
    nearest = [wv.nearest(v, n=nncount, exclude=words) for v in vectors]
    nearest = [[(n[0], n[1], wv[n[0]]) for n in l] for l in nearest]
    assert len(nearest) == 2, 'internal error'
    pairs = [(n1, n2, 
              numpy.dot(wvlib.unit_vector(vectors[1]-vectors[0]+n1[2]), n2[2]))
             for n1 in nearest[0] for n2 in nearest[1] if n1[0] != n2[0]]
    pairs.sort(lambda a, b: cmp(b[2], a[2]))
    nncount = options.number if options else 10
    for p in pairs[:nncount]:
        print '%s\t---\t%s\t%f' % (p[0][0], p[1][0], p[2])
    return True

def main(argv=None):
    if argv is None:
        argv = sys.argv
    options = process_args(argv[1:])
    try:
        wv = wvlib.load(options.vectors, max_rank=options.max_rank)
        wv = wv.normalize()
    except Exception, e:
        print >> sys.stderr, 'Error: %s' % str(e)
        return 1
    return query_loop(wv, options, process_query, query_count=2)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
