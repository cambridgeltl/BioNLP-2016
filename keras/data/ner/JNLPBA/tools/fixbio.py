#!/usr/bin/env python

# Fixes errors in B-I-O sequences in CoNLL-style column-formatted
# data.

from __future__ import with_statement

import sys
import re

__author__ = 'Sampo Pyysalo'
__license__ = 'MIT'

options = None

EMPTY_LINE_RE = re.compile(r'^\s*$')

BIO_TAG_RE = re.compile(r'^([BIO])((?:-\S+)?)$')

def argparser():
    import argparse
    ap=argparse.ArgumentParser(description="Fix B-I-O sequence errors in CoNLL-style data.")
    ap.add_argument("-f", "--first-type", default=False, action="store_true", help="Use first type in for BI+ sequences with multiple types.")
    ap.add_argument("-l", "--last-type", default=False, action="store_true", help="Use first type in for BI+ sequences with multiple types (default).")
    ap.add_argument("-s", "--split-multi", default=False, action="store_true", help="Split BI+ sequences with multiple types (add Bs).")
    ap.add_argument("-i", "--indices", default=None, help="Indices of fields to fix (comma-separated)")
    ap.add_argument("-v", "--verbose", default=False, action="store_true", help="Verbose output.")
    ap.add_argument("files", nargs='+', help="Target file(s) (\"-\" for STDIN)")
    return ap

class ParseError(Exception):
    def __init__(self, line, linenum, message=None, filename=None):
        self.line = line
        self.linenum = linenum
        self.message = message
        self.file = file

        if self.message is None:
            self.message = "Parse error"

    def __str__(self):
        return (self.message +
                ("on line %d" % self.linenum) + 
                ("" if self.file is None else " in file %s" % self.file) +
                (": '%s'" % self.line))

def parse_BIO_tag(tag):
    """Parse given string as BIO tag.

    The expected format is "[BIO]-TYPE", where TYPE is any non-empty
    nonspace string, and the "-TYPE" part is optional.

    Args:
        tag (string): tag to parse.
    Returns:
        string pair: tag ("B", "I" or "O") and TYPE.
    """

    m = re.match(r'^([BIO])((?:-\S+)?)$', tag)
    assert m, "ERROR: failed to parse tag '%s'" % tag
    ttag, ttype = m.groups()

    # Strip off starting "-" from tagged type, if any.
    if len(ttype) > 0 and ttype[0] == "-":
        ttype = ttype[1:]

    return ttag, ttype

def make_BIO_tag(ttag, ttype):
    """Inverse of parse_BIO_tag."""

    if ttype is None:
        return ttag
    else:
        return ttag+'-'+ttype


def is_BIO_tag(s):
    """Return True if given string is a valid BIO tag."""
    return BIO_TAG_RE.match(s)

def BIO_indices(blocks, is_bio=is_BIO_tag):
    """Return indices of fields containing BIO tags.

    Expects output of parse_conll() (or similar) as input.

    Args:
        blocks (list of lists of lists of strings): parsed CoNLL-style input.
        is_bio: function returning True iff given a valid BIO tag.
    Returns:
        list of integers: indices of valid BIO tags in data.
    """

    valid = None
    for block in blocks:
        for line in block:
            # Initialize candidates on first non-empty
            if valid is None:
                valid = range(len(line))

            valid = [i for i in valid if i < len(line) and is_bio(line[i])]

            # Short-circuit
            if len(valid) == 0:
                return valid

    if valid is None:
        return []

    return valid

def _fix_BIO_index(blocks, index):
    """Implement fix_BIO() for single index."""

    global options

    # Fix errors where non-"O" sequence begins with "I" instead of "B"
    for block in blocks:
        prev_tag = None
        for line in block:
            ttag, ttype = parse_BIO_tag(line[index])

            if (prev_tag is None or prev_tag == "O") and ttag == "I":
                if options.verbose:
                    print >> sys.stderr, "Rewriting initial \"I\" -> \"B\" (%s)" % ttype
                line[index] = make_BIO_tag("B", ttype)

            prev_tag = ttag

    # Fix errors where type changes without a "B" at the boundary
    for block in blocks:
        prev_tag, prev_type = None, None
        for ln, line in enumerate(block):
            ttag, ttype = parse_BIO_tag(line[index])

            if prev_tag in ("B", "I") and  ttag == "I" and prev_type != ttype:

                if options.first_type:
                    # Propagate first type to whole sequence
                    if options.verbose:
                        print >> sys.stderr, "Rewriting multi-type sequence to first type (%s->%s)" % (ttype, prev_type)
                    i = ln
                    while i < len(block):
                        itag, itype = parse_BIO_tag(block[i][index])
                        if itag != "I":
                            break
                        block[i][index] = make_BIO_tag(itag, prev_type)
                        i += 1
                    # Current was changed
                    ttype = prev_type

                elif options.last_type:
                    # Propagate last type to whole sequence
                    if options.verbose:
                        print >> sys.stderr, "Rewriting multi-type sequence to last type (%s->%s)" % (prev_type, ttype)
                    i = ln - 1
                    while i >= 0:
                        itag, itype = parse_BIO_tag(block[i][index])
                        if itag not in ("B", "I"):
                            break
                        block[i][index] = make_BIO_tag(itag, ttype)
                        i -= 1

                elif options.split_multi:
                    # Split sequence
                    if options.verbose:
                        print >> sys.stderr, "Rewriting \"I\" -> \"B\" to split at type switch (%s->%s)" % (prev_type, ttype)
                    line[index] = make_BIO_tag("B", ttype)

                else:
                    assert False, "INTERNAL ERROR"
            
            prev_tag, prev_type = ttag, ttype

    return blocks

def fix_BIO(blocks, indices):
    """Corrects BIO tag sequence errors in given data.

    Expects output of parse_conll() (or similar) as input.
    NOTE: Modifies given blocks.

    Args:
        blocks (list of lists of lists of strings): parsed CoNLL-style input.
        indices (list of ints): indices of fields containing BIO tags.
    Returns:
        given blocks with fixed BIO tag sequence.
    """

    assert len(indices) > 0, "Error: fix_BIO() given empty indices"

    for i in indices:
        blocks = _fix_BIO_index(blocks, i)

    return blocks

def _line_is_empty(l):
    return EMPTY_LINE_RE.match(l)

def parse_conll(input, filename=None, separator='\t', is_empty=_line_is_empty):
    """Parse CoNLL-style input.

    Input should consist of blocks of lines separated by empty lines
    (is_empty), each non-empty line consisting of fields separated by
    the given separator.

    Returns:
        list of lists of lists: blocks, lines, fields.
    """

    li, l = 0, None
    try:
        blocks = []
        current_block = []
        for l in input:
            l = l.rstrip()
            li += 1
            if is_empty(l):
                blocks.append(current_block)
                current_block = []
            else:
                current_block.append(l.split(separator))
    except Exception:
        # whatever goes wrong
        raise ParseError(l, li)

    return blocks

def process(input, indices=None):
    blocks = parse_conll(input)

    if indices is None:
        # Fix all valid unless specific indices given
        indices = BIO_indices(blocks)

    assert len(indices) > 0, "Error: no valid BIO fields"
        
    blocks = fix_BIO(blocks, indices)

    # Output
    for block in blocks:
        for line in block:
            print '\t'.join(line)
        print

def process_file(fn, indices=None):
    with open(fn, 'rU') as f:
        return process(f, indices)
        
def main(argv):
    global options

    options = argparser().parse_args(argv[1:])

    # Resolve treatment of BI+ sequences with more than one type
    multi_args = [options.first_type, options.last_type, options.split_multi]
    assert len([a for a in multi_args if a == True]) < 2, 'At most one of the "-f", "-l" and "-s" argument can be specified.'
    if len([a for a in multi_args if a == True]) == 0:
        # Nothing set, default
        options.last_type = True

    # Resolve indices to fix
    if options.indices is None:
        indices = None
    else:
        try:
            indices = [int(i) for i in options.indices.split(",")]
        except Exception:
            assert False, 'Argument "-i" value should be a comma-separated list of integers'

    # Primary processing
    for fn in options.files:
        try:
            if fn == "-":
                # Special case to read STDIN
                process(sys.stdin, indices)
            else:
                process_file(fn, indices)
        except Exception:            
            print >> sys.stderr, "Error processing %s" % fn
            raise

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception, e:
        print >> sys.stderr, e
        sys.exit(1)
