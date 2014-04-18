#!/usr/bin/env python

import os
from canari.maltego.utils import highlight
from canari.pkgutils.transform import TransformDistribution

from common import (canari_main, uproot, pushd)
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
    return args


# Argument parser
@SubCommand(
    canari_main,
    help="Installs and configures canari transform packages in Maltego's UI",
    description="Installs and configures canari transform packages in Maltego's UI"
)
@Argument(
    'package',
    metavar='<package>',
    help='the name of the canari transforms package to install.'
)
@Argument(
    '-w',
    '--working-dir',
    metavar='[working dir]',
    default=None,
    help="the path that will be used as the working directory for "
         "the transforms being installed (default: ~/.canari/)"
)
def list_transforms(args):

    opts = parse_args(args)

    try:
        with pushd(opts.working_dir or os.getcwd()):
            transform_package = TransformDistribution(opts.package)
            for t in transform_package.transforms:
                print ('`- %s: %s' % (highlight(t.__name__, 'green', True), t.dotransform.description))
                print (highlight('  `- Maltego identifiers:', 'black', True))
                for uuid, (input_set, input_type) in zip(t.dotransform.uuids, t.dotransform.inputs):
                    print '    `- %s applies to %s in set %s' % (
                        highlight(uuid, 'red', False),
                        highlight(input_type._type_, 'red', False),
                        highlight(input_set, 'red', False)
                    )
                print ''
    except ValueError, e:
        print str(e)
        exit(-1)