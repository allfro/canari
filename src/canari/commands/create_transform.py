#!/usr/bin/env python

from common import write_template, read_template, cmd_name, init_pkg, project_tree

from argparse import ArgumentParser
from os import path
from re import sub


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Creates a new transform in the specified directory and auto-updates __init__.py.',
    usage='canari %s <transform name> [options]' % cmd_name(__name__)
)

parser.add_argument(
    'transform',
    metavar='<transform name>',
    help='The name of the transform you wish to create.'
)

parser.add_argument(
    '-d',
    '--transform-dir',
    metavar='<dir>',
    help='The directory in which you wish to create the transform.',
    default=None
)


def help_():
    parser.print_help()


def description():
    return parser.description


def parse_args(args):
    args = parser.parse_args(args)
    if args.transform_dir is None:
        args.transform_dir= project_tree()['transforms']
    return args


def run(args):

    opts = parse_args(args)

    initf = path.join(opts.transform_dir, '__init__.py')
    transform = opts.transform if not opts.transform.endswith('.py') else opts.transform[:-3]

    if '.' in transform:
        print "Transform name (%s) cannot have a dot ('.')." % repr(transform)
        exit(-1)
    elif not transform:
        print "You must specify a valid transform name."
        exit(-1)

    directory = opts.transform_dir
    transformf = path.join(directory, opts.transform if opts.transform.endswith('.py') else '%s.py' % opts.transform )

    if not path.exists(initf):
        print ('Directory %s does not appear to be a python package directory... quitting!' % repr(opts.transform_dir))
        exit(-1)
    if path.exists(transformf):
        print ('Transform %s already exists... quitting' % repr(transformf))
        exit(-1)

    values = init_pkg()

    write_template(
        transformf,
        read_template('newtransform', values)
    )

    print ('updating %s' % initf)
    init = file(initf).read()

    with file(initf, mode='wb') as w:
        w.write(
            sub(
                r'__all__\s*\=\s*\[',
                '__all__ = [\n    %s,' % repr(transform),
                init
            )
        )

    print ('done!')
