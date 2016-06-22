#!/usr/bin/env python

"""Evaluate word representations by word set expansion.

The task is to retrieve words from a (nearly) closed set given one or
more example words from the set. Retrieval is based on word vector
similarity (dot product of normalized vectors).
"""

import sys
import os
import re
import codecs
import logging

import wvlib

DEFAULT_ENCODING = 'UTF-8'

SINGLE_WORD_RE = re.compile(r'^(\S+)$')

NEAREST_SEPARATOR_RE = re.compile(r'^\s*$')
NEAREST_QUERY_RE = re.compile(r'^(\S[^\t]*?)\s*$')
NEAREST_RESPONSE_RE = re.compile(r'^(\S[^\t]*?)\t((?:\d*\.)?\d+)$')

verbose = True

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse

    ap=argparse.ArgumentParser()
    ap.add_argument('-a', '--approximate', default=False, action='store_true',
                    help='evaluate using approximate neighbors')
    ap.add_argument('-l', '--list', default=False, action='store_true',
                    help='FILE is nearest-neighbor list')
    ap.add_argument('-n', '--word-number', default=1, metavar='INT', type=int,
                    help='number of words to use for query')
    ap.add_argument('veclist', nargs=1, metavar='VEC/LIST',
                    help='word vectors or nearest-neighbor list')
    ap.add_argument('-v', '--verbose', default=False, action='store_true',
                    help='verbose output')
    ap.add_argument('wordset', nargs='+', help='word sets', metavar='FILE')
    return ap

class FormatError(Exception):
    pass

def parse_word_set_detailed(lines, fn=None):
    targets, accept = set(), set()
    for l in lines:
        if not l or l[0] == '#':
            continue # empty or comment
        f = l.rstrip().split('\t')
        if len(f) % 2:
            raise FormatError('%d fields: %s' % (len(f), l))
        i = 0
        while i < len(f):
            w = f[i+1].strip()
            if f[i] == 'TARGET':
                targets.add(w)
            elif f[i] == 'ALIAS' or f[i] == 'ACCEPT':
                accept.add(w)
            else:
                raise FormatError(l)
            i += 2
    return targets, accept
    
def parse_word_set_simple(lines, fn=None):
    targets = set()
    for l in lines:
        l = l.strip()
        if '\t' in l:
            raise FormatError(l)
        if not l or l[0] == '#':
            continue # empty or comment
        else:
            targets.add(l)
    return targets, set()

def filter_word_set(words, fn=None):
    filtered = set()
    for w in words:
        if SINGLE_WORD_RE.match(w):
            filtered.add(w)
        else:
            logging.warning('%s: skip "%s" (not a single word)' % (fn, w))
    return filtered

def parse_word_set(f, fn=None):
    lines = f.readlines()

    if any(l for l in lines if '\t' in l):
        targets, accept = parse_word_set_detailed(lines, fn)
    else:
        targets, accept = parse_word_set_simple(lines, fn)

    targets = filter_word_set(targets, fn)
    accept = filter_word_set(accept, fn)

    return targets, accept

def read_word_set(fn, encoding=DEFAULT_ENCODING):
    with codecs.open(fn, 'rU', encoding=encoding) as f:
        return parse_word_set(f, fn)

def words_match(w1, w2):
    return w1.lower() == w2.lower()

def contains_matching(words, word):
    return any (words_match(word, w) for w in words)

def query_words(query):
    return query.split()

def evaluate(query, gold, ignore, pred, name):
    matched_gold = dict([(w,False) for w in gold])
    matched_pred = dict([(w,False) for w in pred])
    filter_pred = set()
    for p in pred:
        if contains_matching(query_words(query), p):
            logging.debug('Skip matching: "%s" (for "%s")' % (p, query))
            continue
        if contains_matching(ignore, p):
            logging.debug('Skip ignored: "%s" (for "%s")' % (p, query))
            filter_pred.add(p)
            continue
        for g in gold:
            if words_match(p, g):
                logging.debug('Match "%s" - "%s" (for "%s")' % (p, g, query))
                matched_gold[g] = True
                matched_pred[p] = True
    pred = [p for p in pred if not p in filter_pred]

    if len(pred) > len(gold):
        logging.info('filtering %d predictions to %d for %s' % 
                     (len(pred), len(gold), name))
        pred = pred[:len(gold)]
    elif len(pred) < len(gold) and pred: # don't warn twice for zero (OOV)
        logging.warning('%d gold but only %d predictions for %s' %
                        (len(gold), len(pred), name))

    TPp, TPg, FP, FN = 0, 0, 0, 0
    for p in pred:
        if matched_pred[p]:
            TPp += 1
        else:
            logging.debug('False positive: "%s" (for "%s")' % (p, query))
            FP += 1
            
    for g in gold:
        if matched_gold[g]:
            TPg += 1
        else:
            logging.debug('False negative: "%s" (for "%s")' % (g, query))
            FN += 1

    return TPp, TPg, FP, FN

def prec_rec_F(TPp, TPg, FP, FN):
    if TPp + FP == 0:
        p = 0.0
    else:
        p = 100.0 * TPp / (TPp + FP)
    if TPg + FN == 0:
        r = 0
    else:
        r = 100.0 * TPg / (TPg + FN)
    if p+r == 0:
        F = 0.0
    else:
        F = 2*p*r/(p+r)

    return p, r, F

def report(TPp, TPg, FP, FN, header=None, out=sys.stdout):
    p, r, F = prec_rec_F(TPp, TPg, FP, FN)
    if header is not None:
        out.write(header)
    print >> out, "precision %.2f%% (%d/%d) recall %.2f%% (%d/%d) F %.2f%%" % \
        (p, TPp, TPp+FP, r, TPg, TPg+FN, F)

def evaluate_set(queries, targets, accept, setname, nearest, options):
    tTPp, tTPg, tFP, tFN = 0, 0, 0, 0
    for q in queries:
        if q not in nearest:
            logging.warning('missing nearest, skipping evaluation for "%s"' % q)
            continue
        TPp, TPg, FP, FN = evaluate(q, targets, accept, nearest[q], setname)
        if options.verbose:
            report(TPp, TPg, FP, FN, '%s\t%s: ' % (setname, q))
        tTPp += TPp
        tTPg += TPg
        tFP += FP
        tFN += FN
    report(tTPp, tTPg, tFP, tFN, '%s\tTOTAL: ' % setname)
    return prec_rec_F(tTPp, tTPg, tFP, tFN)

def generate_queries(word_set, n=1):
    # generate n-gram combinations of given words
    words = sorted(list(word_set))
    queries = []
    for i in range(len(words)):
        query = []
        for j in range(n):
            query.append(words[(i+j)%len(words)])
        queries.append(' '.join(query))
    return queries

def unique_elements(sets):
    return set([w for s in sets for w in s])

def check_response(query, response, fn):
    assert query, 'internal error'
    seen, prevd = set(), None
    for r, d in response:
        assert r, 'internal error'
        if r in seen:
            raise FormatError('Error: "%s" occurs twice in %s' % (r, fn))
        seen.add(r)
        if prevd is not None and prevd < d:
            raise FormatError('Error: not sorted by distance for "%s" in %s' % (r, fn))
        prevd = d

def store_nearest_list(nearest, query, response, fn):
    if query is None:
        assert not response, 'Internal error'
    elif query in nearest:
        raise FormatError('Error: "%s" occurs twice in %s' % (query, fn))
    else:
        check_response(query, response, fn)
        nearest[query] = [r[0] for r in response] # ignore distance

def parse_response(l, i, fn):
    m = NEAREST_RESPONSE_RE.match(l)
    assert m, 'internal error'
    rword, dist = m.groups()
    try:
        dist = float(dist)
    except ValueError:
        raise FormatError('Error parsing line %d in %s (not a float): %s' % (i, fn, l))
    return rword, dist

def parse_nearest_lists(f, fn):
    nearest, query, response = {}, None, []
    for i, l in enumerate(f):
        l = l.rstrip('\n')
        if NEAREST_SEPARATOR_RE.match(l):
            store_nearest_list(nearest, query, response, fn)
            query, response = None, []
        elif NEAREST_QUERY_RE.match(l):
            if query is not None:
                raise FormatError('Error parsing line %d in %s: %s' % (i, fn, l))
            query = NEAREST_QUERY_RE.match(l).group(1)
        elif NEAREST_RESPONSE_RE.match(l):
            if query is None:
                raise FormatError('No query word on line %d in %s: %s' % (i, fn, l))
            response.append(parse_response(l, i, fn))
        else:
            raise FormatError('Failed to parse line %d in %s: %s' % (i, fn, l))
    store_nearest_list(nearest, query, response, fn)
    return nearest

def read_nearest_lists(fn, encoding=DEFAULT_ENCODING):
    with codecs.open(fn, 'rU', encoding=encoding) as f:
        return parse_nearest_lists(f, fn)    

def query_vector(wv, words):
    vectors = []
    for w in words:
        if w in wv:
            vectors.append(wv[w])
        else:
            logging.warning('Out of dictionary word: "%s"' % w)
    if len(vectors) == 0:
        return None
    else:
        return wvlib.unit_vector(sum(vectors))

def get_nearest(vectors, queries, nncount=100, options=None):
    nearest = {}
    wv = wvlib.load(vectors).normalize()
    for query in queries:
        words = query.split()
        v = query_vector(wv, words)
        if v is not None:
            if options is None or not options.approximate:
                word_sim = wv.nearest(v, n=nncount, exclude=words)
            else:
                word_sim = wv.approximate_nearest(v, n=nncount, exclude=words,
                                                  evalnum=10*nncount)
            nearest[query] = [ws[0] for ws in word_sim]
        else:
            nearest[query] = [] # out of vocabulary
    return nearest

def evaluate_sets(infn, word_sets, options):
    query_sets = [(generate_queries(t, options.word_number), t, a, n) 
                  for t, a, n in word_sets]
    queries = unique_elements([qs[0] for qs in query_sets])

    # set number of neighbors retrieved heuristically based on the
    # number of targets in the largest set
    nncount = 5 * max(len(targets) for targets, accept, name in word_sets)

    if options.list:
        nearest = read_nearest_lists(infn)
    else:
        nearest = get_nearest(infn, queries, nncount, options)

    results = []
    for queries, targets, accept, name in query_sets:
        p, r, F = evaluate_set(queries, targets, accept, name, nearest, options)
        results.append((p, r, F))
    return sum([F for p, f, F in results])/len(results)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    options = argparser().parse_args(argv[1:])

    if options.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    infn = options.veclist[0]
    word_sets = []
    for fn in options.wordset:
        targets, accept = read_word_set(fn)
        name = os.path.splitext(os.path.basename(fn))[0]
        assert targets, 'Failed to read %s' % fn
        word_sets.append((targets, accept, name))

    avg_F = evaluate_sets(infn, word_sets, options)
    print 'OVERALL AVERAGE:\t%.2f%%\t(F-score)' % avg_F

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

    # runs main() with profiling. To see a profile, run e.g.
    # python -c 'import pstats; pstats.Stats("profile").strip_dirs().sort_stats("time").print_stats()' | less
#    import cProfile
#    cProfile.run('main(sys.argv)', 'profile')
