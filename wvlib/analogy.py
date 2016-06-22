#!/usr/bin/env python

"""Given phrases p1, p2 and p3, find nearest neighbors to
vec(p2)-vec(p1)+vec(p3) in given word representation.

This is a python + wvlib extension of word-analogy.c from word2vec
(https://code.google.com/p/word2vec/). The primary differences to
word-analogy.c are support for additional word vector formats,
increased configurability, and reduced speed.
"""

import sys
import os

import wvlib

from common import process_args, query_loop, output_nearest

def process_query(wv, query, options=None):
    for q in query:
        print q 
    vectors = [wv.words_to_vector(q) for q in query]
    words = [w for q in query for w in q]
    assert len(vectors) == 3, 'internal error'
    vector = wvlib.unit_vector(vectors[1] - vectors[0] + vectors[2])
    nncount = options.number if options else 10
    if options is None or not options.approximate:
        nearest = wv.nearest(vector, n=nncount, exclude=words)
    else:
        nearest = wv.approximate_nearest(vector, n=nncount, exclude=words)
    output_nearest(nearest, options)
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
    return query_loop(wv, options, process_query, query_count=3)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
