#!/usr/bin/env python

import os
from canari.utils.console import highlight
from canari.pkgutils.transform import TransformDistribution

from common import (canari_main, pushd, project_tree)
from framework import SubCommand, Argument


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = ['Jesper Reenberg']

__license__ = 'GPL'
__version__ = '0.6'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


def parse_args(args):
    args.ptree = project_tree(package = args.package)
    args.package = args.ptree['pkg_name']
    # We specifically don't update 'args' with any of the info from ptree.  This
    # way we always know exactly what information was specified by the user.
    return args

# Argument parser
@SubCommand(
    canari_main,
    help="List transforms inside the given transform package",
    description="List transforms inside a given transform package (<package>).  "
        "Python 'import' ordering is used, thus a specified directory (--dir) "
        "will supersede the current working directory which superseeds installed "
        "packages, as long as a canari project is found in any of the two.  If "
        "no package name is specified, then all possible transform packages "
        "inside the found canari project is listed."
)
@Argument(
    'package',
    metavar='<package>',
    nargs='?',
    default=None,
    help="the name of the canari transform package to list transforms from.  If"
        "no canari project is located, then the installed modules is searched."
)
@Argument(
    '-d',
    '--dir',
    metavar='[dir]',
    default=os.getcwd(),
    help="if supplied, the path will owerwrite the current working directory when "
         "searching for canari projects."
)


def list_transforms(args):

    # TODO: project_tree may raise an exception if either project_root can't be
    # determined or if we can't find the package as an installed package.
    # Atleast the create-transform command calls this function without handling
    # the possible exception.  What is the best sollution?

    # TODO: create-transform takes an argument --transform-dir which can be used
    # to control where to place the transform template. This breaks the new
    # assumption of the 'transforms' folder always being inside the 'pkg'
    # folder.  However this is an assumption all over the place, so this
    # parameter doesn't really make much sense?

    # TODO: There are most likely many commands with similar problems
    # (above). and perhaps they should be updated to use the below template and
    # have their argument updated to -d/--dir instead with CWD as the default
    # value.

    # TODO: Perhaps we should introduce a 'create' command that will just make
    # an empty canari root dir (project). Inside this we can then call
    # create-package a number of times to generate all the desired
    # packages. This could even be automated for N-times during the call to
    # 'create'. 'create-package' can even still default to call 'create' if not
    # inside a canari root directory, to preserve backwards compatability.

    # TODO: Handle hyphening of package names. When creating them and when
    # trying to access them.  This goes for project_tree, it should change '-'
    # with '_' in the package name.

    try:
        with pushd(args.dir):
            opts = parse_args(args)

        with pushd(args.ptree['src']):

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
