#!/usr/bin/env python

"""Find nearest neighbors to input word(s) in given word representation.

This is a python + wvlib version of distance.c from word2vec
(https://code.google.com/p/word2vec/). The primary differences to
distance.c are support for additional word vector formats, increased
configurability, and reduced speed.
"""

import sys
import os

import wvlib

from common import process_args, query_loop, output_nearest

def process_query(wv, query, options=None):
    words = [w for q in query for w in q]
    vector = wv.words_to_vector(words)
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
    return query_loop(wv, options, process_query)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
