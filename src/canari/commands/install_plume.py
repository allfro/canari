#!/usr/bin/env python
import os

from argparse import ArgumentParser

from common import read_template, write_template, build_skeleton, cmd_name


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

parser = ArgumentParser(
    description='Sets up Canari Plume directory structure and configuration files.',
    usage='canari %s [--install-dir <dir>]' % cmd_name(__name__)
)

parser.add_argument(
    '-d',
    '--install-dir',
    metavar='<dir>',
    help='The name of the canari package you wish to create.',
    default=os.getcwd()
)


def write_setup(base_dir, values):
    plume_sh = os.path.join(base_dir, 'plume.sh')
    write_template(os.path.join(base_dir, 'canari.conf'), read_template('canari', values))
    write_template(os.path.join(base_dir, 'plume.py'), read_template('plume_wsgi', values))
    write_template(plume_sh, read_template('plume_sh', values))
    os.chmod(plume_sh, 0755)


def help_():
    parser.print_help()


def description():
    return parser.description


def run(args):
    opts = parser.parse_args(args)

    install_dir = opts.install_dir
    base_dir = os.path.join(install_dir, 'plume')

    values = dict(
        working_dir=base_dir,
        config='',
        path='${PATH},/usr/local/bin,/opt/local/bin' if os.name == 'posix' else '',
        command=' '.join(['canari deploy-plume'] + args)
    )

    if not os.path.exists(install_dir):
        print('Installation path %s does not exist.' % install_dir)
        exit(-1)
    if not os.path.exists(base_dir):
        print('creating skeleton in %s' % base_dir)
        build_skeleton(
            base_dir,
            [base_dir, 'static']
        )
    else:
        print('A Plume installation at path %s already exists... exiting' % base_dir)
        exit(-1)

    write_setup(base_dir, values)

    print('done!')

    print('Please edit $PLUME_USER, $PLUME_GROUP, $PLUME_PORT in plume.sh prior to running starting Plume.')