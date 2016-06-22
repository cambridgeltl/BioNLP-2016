import inspect
import argparse
import re

from json import dumps
from hashlib import md5

def from_cli(positional, optional, argv=None):
    """Return CLI arguments."""
    if argv is None:
        import sys
        argv = sys.argv
    parser = argparser(positional, optional)
    args = parser.parse_args(argv[1:])
    return args

def serialize(settings, exclude=None):
    """Return a consistent, human-readable string serialization of settings."""
    if exclude is None:
        exclude = []
    sdict = dict(_variables(settings))
    sdict = { k: v for k, v in sdict.items() if k not in exclude }
    sstr = dumps(sdict, sort_keys=True, indent=4, separators=(',', ': '))
    # Remove linebreaks from values (nicer layout)
    while True:
        snew = re.sub(r'\n\s*([^"\s\}])', r' \1', sstr)
        if snew == sstr:
            break
        sstr = snew
    return sstr

def checksum(settings, exclude=None):
    sstr = serialize(settings, exclude)
    return md5(sstr).hexdigest()

def log_with(settings, logger):
    # Record also checksum for settings without datadir to make it
    # easier to identify logs for same settings and different data
    checksums = checksum(settings) + ' / ' + checksum(settings, 'datadir')
    logger('settings:'+checksums+'\n'+serialize(settings))

def argparser(positional, optional):
    """Return ArgumentParser."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    add = parser.add_argument
    for arg in positional:
        add(arg)
    # take optional args and defaults from arguments class variables and values
    for arg, val in _variables(optional):
        name, help_ = arg.replace('_', '-'), arg.replace('_', ' ')
        type_ = type(val) if val is not None else int    # assume int for None
        if type_ in (int, float, str):
            add('--'+name, metavar=_typename(val), type=type_, default=val,
                help=help_)
        elif type_ is list:
            add('--'+name, metavar=_typename(val), type=type(val[0]),
                nargs='+', default=val, help=help_)
        elif type_ is bool:
            name = 'no-'+name if val else name
            act = 'store_' + ('false' if val else 'true')
            add('--'+name, dest=arg, default=val, action=act,
                help='toggle ' + help_)
        else:
            raise NotImplementedError(type_.__name__)
    return parser

def _variables(cls, include_special=False):
    """Return class variables."""
    vars = inspect.getmembers(cls, lambda m: not inspect.isroutine(m))
    if not include_special:
        vars = [v for v in vars if not (v[0].startswith('__') and
                                        v[0].endswith('__'))]
    return vars

def _typename(d):
    d = d[0] if type(d) is list else d
    t = type(d) if d is not None else int
    return t.__name__.upper()
