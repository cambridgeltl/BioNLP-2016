#!/usr/bin/env python

"""Convert between word vector formats."""

import sys
import logging
import wvlib

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse

    ap=argparse.ArgumentParser()
    ap.add_argument('input', metavar='INFILE', help='input vector file')
    ap.add_argument('output', metavar='OUTFILE', help='output vector file')
    ap.add_argument('-i', '--input-format', default=None, 
                    choices=wvlib.formats, help='input FILE format')
    ap.add_argument('-n', '--normalize', default=False, action='store_true',
                    help='normalize vectors to unit length')
    # only wvlib output supported at the moment
#     ap.add_argument('-o', '--output-format', default=None,
#                     choices=wvlib.output_formats, help='output FILE format')
    ap.add_argument('-r', '--max-rank', metavar='INT', default=None, 
                    type=int, help='only load r most frequent words')
    ap.add_argument('-v', '--vector-format', default=None, 
                    choices=wvlib.vector_formats,
                    help='output vector format (with wvlib output)')
    return ap

def main(argv=None):
    if argv is None:
        argv = sys.argv

    options = argparser().parse_args(argv[1:])
    if options.max_rank is not None and options.max_rank < 1:
        raise ValueError('max-rank must be >= 1')

    wv = wvlib.load(options.input, options.input_format,
                    max_rank=options.max_rank)

    if options.normalize:
        logging.info('normalize vectors to unit length')
        wv.normalize()

    wv.save(options.output, vector_format=options.vector_format)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
