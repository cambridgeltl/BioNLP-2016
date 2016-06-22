#!/usr/bin/env python

"""Common support functions for wvlib command-line scripts."""

import sys
import logging

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('vectors', metavar='FILE', help='word vectors')
    ap.add_argument('-a', '--approximate', default=False, action='store_true',
                    help='search by approximate similarity')
    ap.add_argument('-e', '--echo', default=False, action='store_true',
                    help='echo query word(s)')
    ap.add_argument('-m', '--multiword', default=False, action='store_true',
                    help='multiword input')
    ap.add_argument('-n', '--number', metavar='INT', default=40, type=int,
                    help='number of nearest words to retrieve')
    ap.add_argument('-r', '--max-rank', metavar='INT', default=None, 
                    type=int, help='only consider r most frequent words')
    ap.add_argument('-q', '--quiet', default=False, action='store_true',
                    help='minimal output')
    ap.add_argument('-x', '--exit-word', default='EXIT',
                    help='exit on word (default "EXIT")')
    return ap

def process_args(args, prompt='Enter words'):    
    options = argparser().parse_args(args)
    if options.quiet:
        logging.getLogger().setLevel(logging.WARN)
        options.prompt = ''
    elif not options.exit_word:
        options.prompt = prompt + ' (CTRL-D to break):\n'
    else:
        options.prompt = prompt + ' (%s or CTRL-D to break):\n' % \
            options.exit_word
    if options.max_rank is not None and options.max_rank < 1:
        raise ValueError('max-rank must be >= 1')
    return options

def get_line(prompt, exit_word=None):
    try:
        s = raw_input(prompt)
    except KeyboardInterrupt:   # CTRL-C
        raise EOFError
    if s.strip() == exit_word:
        raise EOFError('exit word in input')
    return s

def get_query(prompt='', multiword=False, exit_word=None, max_phrases=None):
    """Return query from user input.

    Input is returned as one or more lists of words (phrases), for
    example

        [["paris"], ["france"], ["tokyo"]]

    or

        [["new", "york"], ["united", "states"], ["kuala lumpur"]

    If multiword evaluates to False, prompt for one phrase of single
    words, otherwise prompts for up to max_phrases of one or more
    words. Return None on end of input or if exit_word is given as
    input.
    """
    
    if not multiword:
        query = [[w] for w in get_line(prompt, exit_word).split()]
    else:
        query = [get_line(prompt, exit_word).split()]
        while True:
            line = get_line('', exit_word)
            if not line or line.isspace():
                break
            query.append(line.split())
            if max_phrases and len(query) >= max_phrases:
                break
    return query

def empty_query(query):
    return not query or not any(p for p in query)

def uniq(items):
    seen = set()
    return [i for i in items if not (i in seen or seen.add(i))]

def query_loop(wv, options, process_query, query_count=1):
    while True:
        try:
            query = get_query(options.prompt, options.multiword, 
                              options.exit_word, query_count)
        except EOFError:
            return 0
        if empty_query(query):
            continue
        if options.echo:
            print query
        if len(query) < query_count:
            print >> sys.stderr, 'Enter %d words/phrases' % query_count
            continue
        if len(query) > query_count:
            print >> sys.stderr, 'Ignoring extra words/phrases'
            query = query[:query_count]
        words, missing = [w for q in query for w in q], []
        for w in uniq(words):
            if w not in wv:
                print >> sys.stderr, 'Out of dictionary word: %s' % str(m)
                missing.add(w)
            elif not options.quiet:
                print 'Word: %s  Position in vocabulary: %d' % (w, wv.rank(w))
        if not missing:
            process_query(wv, query, options)

def output_nearest(nearest, options, out=sys.stdout):
    # word2vec distance.c output header
    output_header = '\n'+46*' '+'Word       Cosine distance\n'+72*'-'
    if not options.quiet:
        print >> out, output_header
        fmt = '%50s\t\t%f'
    else:
        fmt = '%s\t%f'
    for w, s in nearest:
        print >> out, fmt % (w, s)
    print >> out
