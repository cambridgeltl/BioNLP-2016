#!/usr/bin/env python

"""Output similarity between words in input."""

import sys

import numpy
import wvlib

from common import process_args, query_loop

def process_query(wv, query, options=None):
    vectors = [wv.words_to_vector(q) for q in query]
    words = [w for q in query for w in q]
    assert len(vectors) == 2, 'internal error'
    vectors = [v/numpy.linalg.norm(v) for v in vectors]
    print numpy.dot(vectors[0], vectors[1])
    
def process_query1(wv, query, options=None):
    try:
        vectors = [wv.words_to_vector(q) for q in query]
        words = [w for q in query for w in q]
        assert len(vectors) == 2, 'internal error'
        vectors = [v/numpy.linalg.norm(v) for v in vectors]
        #print numpy.dot(vectors[0], vectors[1])
        return numpy.dot(vectors[0], vectors[1])

    except KeyError:
        return -1
        #print "key Error"
        
def main(argv=None):
    if argv is None:
        argv = sys.argv
    # TODO: remove irrelevant options
    options = process_args(argv[1:])
    try:
        wv = wvlib.load(options.vectors, max_rank=options.max_rank)
    except Exception, e:
        print >> sys.stderr, 'Error: %s' % str(e)
        return 1
    return query_loop(wv, options, process_query, query_count=2)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
