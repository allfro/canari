#!/usr/bin/env python

from common import cmd_name, project_tree

from argparse import ArgumentParser
from os import path, rename
from re import sub


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Renames a transform in the specified directory and auto-updates __init__.py.',
    usage='canari %s <transform name> [options]' % cmd_name(__name__)
)

parser.add_argument(
    'transform',
    metavar='<old transform name>',
    help='The name of the transform you wish to rename.'
)

parser.add_argument(
    'new_transform',
    metavar='<new transform name>',
    help='The desired name of the transform.'
)

parser.add_argument(
    '-d',
    '--transform-dir',
    metavar='<dir>',
    help='The directory from which you wish to rename the transform.',
    default=None
)


def help_():
    parser.print_help()


def description():
    return parser.description


def parse_args(args):
    args = parser.parse_args(args)
    if args.transform_dir is None:
        args.transform_dir = project_tree()['transforms']
    return args


def run(args):

    opts = parse_args(args)

    initf = path.join(opts.transform_dir, '__init__.py')
    transform = opts.transform
    transformf = path.join(opts.transform_dir, transform if transform.endswith('.py') else '%s.py' % transform )
    dtransform = opts.new_transform
    dtransformf = path.join(opts.transform_dir, dtransform if dtransform.endswith('.py') else '%s.py' % dtransform )

    if not path.exists(initf):
        print ('Directory %s does not appear to be a python package directory... quitting!' % repr(opts.transform_dir))
        exit(-1)
    if not path.exists(transformf):
        print ("Transform %s doesn't exists... quitting" % repr(transformf))
        exit(-1)
    if path.exists(dtransformf):
        print ("Cannot overwrite existing transform %s... quitting" % repr(dtransformf))
        exit(-1)
    if dtransform == transform:
        print ("Nothing to do here... the new name is the same as the old one?")
        exit(-1)

    print ('renaming transform %s to %s...' % (repr(transformf), repr(dtransformf)))
    rename(transformf, dtransformf)

    print ('updating %s' % initf)
    init = file(initf).read()

    with file(initf, mode='wb') as w:
        w.write(
            sub(
                repr(transform),
                repr(dtransform),
                init
            )
        )

    print ('done!')
