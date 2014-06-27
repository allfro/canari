#!/usr/bin/env python

import os
from canari.maltego.utils import highlight
from canari.pkgutils.transform import TransformDistribution

from common import (canari_main, uproot, pushd, project_tree)
from framework import SubCommand, Argument


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.6'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


# Extra sauce to parse args
def parse_args(args):
    try:
        ptree = project_tree()
    except Exception as ex:
        print "Got exception while trying to determine the project root. " \
              "Supply a proper --src-dir argument."
        print 'Exception:', highlight(str(ex), 'red', False)
        exit(-1)

    if args.src_dir is None:
        args.src_dir = ptree['src']
    if args.package is None:
        _, args.package = ptree['pkg'].rsplit(os.path.sep, 1)

    return args


# Argument parser
@SubCommand(
    canari_main,
    help="List transforms inside the given transform package.",
    description="List transforms inside the given transform package."
)
@Argument(
    'package',
    metavar='<package>',
    nargs='?',
    default=None,
    help="the name of the canari transform package to list transforms from. "
         "Python 'import' ordering is used, thus a specified working directory "
         "will supersede any installed packages. If not specified, the package "
         "name will be read from the project configuration if --src-dir or the "
         "current working directory is a valid transform package."
)
@Argument(
    '-d',
    '--src-dir',
    metavar='[src dir]',
    default=None,
    help="the path that will be used when looking for the transform package "
         "(<package>). Should point to the source folder (src) containing the "
         "specified transform package. If not specified, it will try and guess "
         "the src folder or use the current working directory as a fall back."
)
def list_transforms(args):

    opts = parse_args(args)

    try:
        with pushd(opts.src_dir or os.getcwd()):
            transform_package = TransformDistribution(opts.package)
            for t in transform_package.transforms:
                print ('`- %s: %s' % (highlight(t.__name__, 'green', True),
                                      t.dotransform.description))
                print (highlight('  `- Maltego identifiers:', 'black', True))
                for uuid, (input_set, input_type) in zip(t.dotransform.uuids,
                                                         t.dotransform.inputs):
                    print '    `- %s applies to %s in set %s' % (
                        highlight(uuid, 'red', False),
                        highlight(input_type._type_, 'red', False),
                        highlight(input_set, 'red', False)
                    )
                print ''
    except ValueError as e:
        print str(e)
        exit(-1)
