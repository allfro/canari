__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


#!/usr/bin/env python

import os
from string import Template

from pkg_resources import resource_filename
from argparse import ArgumentParser

from common import cmd_name, import_transform, import_package, parse_bool
from canari.config import CanariConfigParser


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


# Dictionary of detected transforms
transforms = {}

# Argument parser
parser = ArgumentParser(
    description="Loads a canari package into Plume.",
    usage='canari %s <package>' % cmd_name(__name__)
)

parser.add_argument(
    'package',
    metavar='<package>',
    help='the name of the canari transforms package to load into Plume.'
)
parser.add_argument(
    '-d',
    '--plume-dir',
    metavar='[www dir]',
    default=os.getcwd(),
    help='the path where Plume is installed.'
)


# Help for this command
def help_():
    parser.print_help()


def description():
    return parser.description


# Extra sauce to parse args
def parse_args(args):
    return parser.parse_args(args)


def writeconf(sf, df, **kwargs):
    if not os.path.exists(df):
        print ('Writing %s to %s' % (sf, df))
        with file(df, mode='wb') as w:
            if 'sub' in kwargs and kwargs['sub']:
                del kwargs['sub']
                w.write(
                    Template(
                        file(
                            sf
                        ).read()
                    ).substitute(**kwargs)
                )
            else:
                w.write(
                    file(
                        sf
                    ).read()
                )


def updateconf(opts, canari_conf):
    ld = os.getcwd()
    os.chdir(os.path.dirname(canari_conf))

    config = CanariConfigParser()
    config.read(canari_conf)
    configs = config['default/configs']
    packages = config['remote/packages']

    conf = '%s.conf' % opts.package

    if isinstance(configs, basestring):
        configs = [configs] if configs else []

    if isinstance(packages, basestring):
        packages = [packages] if packages else []

    if conf not in configs:
        print ('Updating %s...' % canari_conf)
        configs.append(conf)
        config['default/configs'] = ','.join(configs)

    if opts.package not in packages:
        packages.append(opts.package)
        config['remote/packages'] = ','.join(packages)

    config.write(file(canari_conf, mode='wb'))
    os.chdir(ld)


def installconf(opts, args):
    src = resource_filename('canari.resources.template', 'canari.plate')
    writeconf(
        src,
        os.path.join(opts.plume_dir, 'canari.conf'),
        sub=True,
        command=' '.join(['canari install'] + args),
        config=('%s.conf' % opts.package) if opts.package != 'canari' else '',
        path='${PATH},/usr/local/bin,/opt/local/bin' if os.name == 'posix' else ''
    )

    if opts.package != 'canari':
        src = resource_filename('%s.resources.etc' % opts.package, '%s.conf' % opts.package)
        writeconf(src, os.path.join(opts.plume_dir, '%s.conf' % opts.package), sub=False)
        updateconf(opts, os.path.join(opts.plume_dir, 'canari.conf'))

# Main
def run(args):

    opts = parse_args(args)

    if not os.path.exists(os.path.join(opts.plume_dir, 'plume.py')):
        print('Plume does not appear to be installed in %s.' % opts.plume_dir)
        ans = parse_bool("Would you like to install it [Y/n]: ")
        if not ans:
            print 'Installation cancelled. Quitting...'
            exit(-1)
        os.system('canari install-plume --install-dir %s' % opts.plume_dir)
        opts.plume_dir = os.path.join(opts.plume_dir, 'plume')


    if opts.package.endswith('.transforms'):
        opts.package = opts.package.replace('.transforms', '')


    print ('Looking for transforms in %s.transforms' % opts.package)
    transform_package = None
    try:
        transform_package = import_package('%s.transforms' % opts.package)
    except ImportError, e:
        print ("Does not appear to be a valid canari package. "
               "Couldn't import the '%s.transforms' package in '%s'. Error message: %s" %
               (opts.package, opts.package, e))
        exit(-1)

    for t in transform_package.__all__:
        transform_module = import_transform('%s.transforms.%s' % (opts.package, t))
        if hasattr(transform_module, 'dotransform') and hasattr(transform_module.dotransform, 'remote'):
            print('Loaded.')
            try:
                print('Writing config to %s...' % opts.plume_dir)
                installconf(opts, args)
            except ImportError:
                pass
            print('Please restart plume (./plume.sh restart) for changes to take effect.')
            exit(0)

    print ('Error: no remote transforms found. '
           'Please make sure that at least one transform has remote=True in @configure before retrying.')
    exit(-1)
