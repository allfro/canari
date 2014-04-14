#!/usr/bin/env python

import os
import re

from common import write_template, read_template, canari_main, init_pkg, project_tree
from framework import SubCommand, Argument

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


def parse_args(args):
    if args.transform_dir is None:
        args.transform_dir = project_tree()['transforms']
    if args.transform in ['common', 'common.py']:
        print "Error: 'common' is a reserved module. Please name your transform something else."
        exit(-1)
    return args


@SubCommand(
    canari_main,
    help='Creates a new transform in the specified directory and auto-updates __init__.py.',
    description='Creates a new transform in the specified directory and auto-updates __init__.py.'
)
@Argument(
    'transform',
    metavar='<transform name>',
    help='The name of the transform you wish to create.'
)
@Argument(
    '-d',
    '--transform-dir',
    metavar='<dir>',
    help='The directory in which you wish to create the transform.',
    default=None
)
def create_transform(args):

    opts = parse_args(args)

    initf = os.path.join(opts.transform_dir, '__init__.py')
    transform = opts.transform if not opts.transform.endswith('.py') else opts.transform[:-3]

    if '.' in transform:
        print "Transform name (%s) cannot have a dot ('.')." % repr(transform)
        exit(-1)
    elif not transform:
        print "You must specify a valid transform name."
        exit(-1)

    directory = opts.transform_dir
    transformf = os.path.join(directory, opts.transform if opts.transform.endswith('.py') else '%s.py' % opts.transform )

    if not os.path.exists(initf):
        print ('Directory %s does not appear to be a python package directory... quitting!' % repr(opts.transform_dir))
        exit(-1)
    if os.path.exists(transformf):
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
            re.sub(
                r'__all__\s*\=\s*\[',
                '__all__ = [\n    %s,' % repr(transform),
                init
            )
        )

    print ('done!')
