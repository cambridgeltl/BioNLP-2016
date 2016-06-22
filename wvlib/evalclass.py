#!/usr/bin/env python

"""Evaluate word representations by example-based classification.

The task is to classify a word into one of two candidate sets based on
its similarity (dot product of normalized vectors) to example words of
those classes.

The full evaluation is as follows. Given word vectors and two or more
sets of words that are members of some class (e.g. "countries"),
consider all pairs of word sets, and for each pair consider all
combinations consisting of one example word from each set and a test
word from one. Performance is reported as accuracy per word set pair
and summarized as macroaverage over the pairs.

NOTE: Out-of-vocabulary words are removed prior to processing. Results
for representations induced from different datasets or settings may
thus not be comparable. In particular, it is likely possible to
improve evaluation results by excluding more rare words.
"""

import sys
import os
import numpy
import codecs
import logging

from itertools import combinations

import wvlib

ENCODING = 'UTF-8'

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse

    ap=argparse.ArgumentParser()
    ap.add_argument('-r', '--max-rank', metavar='INT', default=None, 
                    type=int, help='only consider r most frequent words')
    ap.add_argument('-q', '--quiet', default=False, action='store_true')
    ap.add_argument('vectors', nargs=1, help='word2vec word vectors')
    ap.add_argument('wordset', nargs='+', help='word sets', metavar='FILE')
    return ap

def read_words(fn, encoding=ENCODING):
    words = []
    with codecs.open(fn, 'rU', encoding=encoding) as f:
        for l in f:
            w = l.rstrip()
            if ' ' in w:
                print >> sys.stderr, 'Skip multiword: "%s"' % w
                continue
            words.append(w)
    return words

def read_wordsets(fns):
    wordsets = {}
    for fn in fns:
        base = os.path.basename(fn).replace('.txt', '')
        assert base not in wordsets, 'duplicate wordset file %s' % base
        words = read_words(fn)
        if len(words) < 1:
            logging.warning('no words read from %s' % fn)
        else:
            wordsets[base] = words
    return wordsets

def enough_data(wordsets):
    assert not any(s for s in wordsets if len(s) == 0), 'empty set'
    if len(wordsets) < 2:
        print >> sys.stderr, 'error: at least two non-empty word sets required'
        argparser().print_help()
        return False
    else:
        return True

FIRST, SECOND, UNDEF = range(3)
def closer(w1, w2, w, w2v):
    d1 = numpy.dot(w2v[w1], w2v[w])
    d2 = numpy.dot(w2v[w2], w2v[w])
    if d1 > d2:
        return FIRST
    elif d1 < d2:
        return SECOND
    else:
        return UNDEF

def score(w1, w2, w, w2v, answer):
    pred = closer(w1, w2, w, w2v)
    if pred == answer:
        return 1.0
    elif pred == UNDEF:
        return 0.5
    else:
        return 0.0

def compare_sets(set1, name1, set2, name2, w2v, options=None):
    total, correct = 0, 0
    for w1 in set1:
        for w2 in set2:
            for w in (x for x in set1 if x != w1):
                correct += score(w1, w2, w, w2v, FIRST)
                total += 1
            for w in (x for x in set2 if x != w2):
                correct += score(w1, w2, w, w2v, SECOND)
                total += 1
    if not total:
        print >> sys.stderr, '%s - %s: No comparisons succeeded!' % \
            (name1, name2)
        return None
    else:
        avg = 1.*correct/total
        if not options or not options.quiet:
            print 'AVERAGE %s - %s: %.2f%% (%d/%d)' % \
                (name1, name2, 100*avg, correct, total)
        return avg
        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    options = argparser().parse_args(argv[1:])

    if options.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    wordsets = read_wordsets(options.wordset)

    if not enough_data(wordsets):
        return 1

    if options.max_rank is not None and options.max_rank < 1:
        raise ValueError('max-rank must be >= 1')
    wv = wvlib.load(options.vectors[0], max_rank=options.max_rank).normalize()
    w2v = wv.word_to_vector_mapping()

    word_count, oov_count = 0, 0
    filtered_wordsets = {}
    for k, wordset in wordsets.items():
        filtered = []
        for w in wordset:
            if w in w2v:
                filtered.append(w)
            else:
                logging.warn('ignoring out-of-vocabulary word "%s"' % w)
                oov_count += 1
            word_count += 1
        if filtered:
            filtered_wordsets[k] = filtered
        else:
            logging.warn('wordset %s empty after OOV filtering, removing' % k)
    wordsets = filtered_wordsets
            
    if not enough_data(wordsets):
        return 1

    results = []
    for n1, n2 in combinations(wordsets.keys(), 2):
        result = compare_sets(wordsets[n1], n1, wordsets[n2], n2, w2v, options)
        if result is not None:
            results.append(result)

    if not options.quiet:
        print >> sys.stderr, 'out of vocabulary %d/%d (%.2f%%)' % \
            (oov_count, word_count, 100.*oov_count/word_count)

    if results:
        print 'OVERALL AVERAGE (macro):\t%.2f%%\t(%.2f%% OOV)' % \
            (100*sum(results)/len(results), 100.*oov_count/word_count)
    else:
        print >> sys.stderr, 'All comparisons failed!'

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
    # runs main() with profiling. To see a profile, run e.g.
    # python -c 'import pstats; pstats.Stats("profile").strip_dirs().sort_stats("time").print_stats()' | less
#    import cProfile
#    cProfile.run('main(sys.argv)', 'profile')
