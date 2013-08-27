#!/usr/bin/env python

from common import detect_settings_dir, cmd_name, fix_pypath, import_package, import_transform, fix_etree, maltego_version

from xml.etree.cElementTree import ElementTree, XML
from os import path, mkdir, listdir, unlink, rmdir
from pkg_resources import resource_listdir
from argparse import ArgumentParser


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


# Argument parser
parser = ArgumentParser(
    description="Uninstalls and unconfigures canari transform packages in Maltego's UI",
    usage='canari %s <package> [options]' % cmd_name(__name__)
)

parser.add_argument(
    'package',
    metavar='<package>',
    help='the name of the canari transforms package to uninstall.'
)
parser.add_argument(
    '-s',
    '--settings-dir',
    metavar='[settings dir]',
    default=detect_settings_dir,
    help='the path to the Maltego settings directory (automatically detected if excluded)'
)


def help_():
    parser.print_help()


def description():
    return parser.description


def uninstallnbattr(machine, xml):
    e = xml.find('fileobject[@name="%s"]' % machine)
    if e is not None:
        xml.remove(e)

def uninstallmachines(package, prefix):
    try:
        prefix = path.join(prefix, 'config', 'Maltego', 'Machines')
        n = path.join(prefix, '.nbattrs')
        e = XML('<attributes version="1.0"/>')
        if path.exists(n):
            e = XML(file(n).read())
        if not path.exists(prefix):
            return
        package = '%s.resources.maltego' % package
        for m in filter(lambda x: x.endswith('.machine'), resource_listdir(package, '')):
            print 'Uninstalling machine %s...' % m
            try:
                unlink(path.join(prefix, m))
                uninstallnbattr(m, e)
            except OSError:
                pass
        ElementTree(e).write(file(n, 'wb'))
    except ImportError, e:
        pass


def uninstall_transform(module, spec, prefix):

    installdir = path.join(prefix, 'config', 'Maltego', 'TransformRepositories', 'Local')

    if not path.exists(installdir):
        mkdir(installdir)

    setsdir = path.join(prefix, 'config', 'Maltego', 'TransformSets')

    for i,n in enumerate(spec.uuids):

        print ('Uninstalling transform %s from %s...' % (n, module))

        if spec.inputs[i][0] is not None:
            setdir = path.join(setsdir, spec.inputs[i][0])
            f = path.join(setdir, n)
            if path.exists(f):
                unlink(f)
            if path.exists(setdir) and not listdir(setdir):
                rmdir(setdir)

        tf = path.join(installdir, '%s.transform' % n)
        tsf = path.join(installdir, '%s.transformsettings' % n)

        if path.exists(tf):
            unlink(tf)
        if path.exists(tsf):
            unlink(tsf)


def parse_args(args):
    args = parser.parse_args(args)
    if args.settings_dir is detect_settings_dir:
        args.settings_dir = detect_settings_dir()
    if maltego_version(args.settings_dir) >= '3.4.0':
        print("""
=========================== ERROR: NOT SUPPORTED ===========================

 Starting from Maltego v3.4.0 the 'canari uninstall-package' command is no
 longer supported. Please use the Maltego interface to uninstall packages.

=========================== ERROR: NOT SUPPORTED ===========================
        """)
        exit(-1)
    return args


def run(args):

    opts = parse_args(args)

    if opts.package.endswith('.transforms'):
        opts.package = opts.package.replace('.transforms', '')

    fix_pypath()

    fix_etree()

    m = import_package('%s.transforms' % opts.package)

    for t in m.__all__:
        transform = '%s.transforms.%s' % (opts.package, t)
        m2 = import_transform(transform)
        if hasattr(m2, 'dotransform') and hasattr(m2.dotransform, 'label'):
            uninstall_transform(
                m2.__name__,
                m2.dotransform,
                opts.settings_dir
            )

    uninstallmachines(opts.package, opts.settings_dir)
