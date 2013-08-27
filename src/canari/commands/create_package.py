#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from getpass import getuser
from os import path

from common import read_template, write_template, generate_all, build_skeleton, cmd_name, parse_bool
import canari


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.7'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

parser = ArgumentParser(
    description='Creates a Canari transform package skeleton.',
    usage='canari %s <package name>' % cmd_name(__name__)
)

parser.add_argument(
    'package',
    metavar='<package name>',
    help='The name of the canari package you wish to create.'
)


def write_setup(package_name, values):
    write_template(path.join(package_name, '.canari'), read_template('_canari', values))
    write_template(path.join(package_name, 'setup.py'), read_template('setup', values))
    write_template(path.join(package_name, 'README.md'), read_template('README', values))
    write_template(path.join(package_name, 'MANIFEST.in'), read_template('MANIFEST', values))


def write_root(base, init):
    write_template(
        path.join(base, '__init__.py'),
        init + generate_all('resources', 'transforms')
    )


def write_resources(package_name, resources, init, values):
    write_template(
        path.join(resources, '__init__.py'),
        init + generate_all('etc', 'images', 'maltego', 'external')
    )

    write_template(
        path.join(resources, 'etc', '__init__.py'),
        init
    )

    write_template(
        path.join(resources, 'images', '__init__.py'),
        init
    )

    write_template(
        path.join(resources, 'external', '__init__.py'),
        init
    )

    write_template(
        path.join(resources, 'maltego', '__init__.py'),
        init
    )

    write_template(
        path.join(resources, 'etc', '%s.conf' % package_name),
        read_template('conf', values)
    )


def write_common(transforms, init, values):
    if values['example']:
        write_template(
            path.join(transforms, '__init__.py'),
            init + generate_all('common', 'helloworld')
        )

        write_template(
            path.join(transforms, 'helloworld.py'),
            read_template('transform', values)
        )
    else:
        write_template(
            path.join(transforms, '__init__.py'),
            init + generate_all('common')
        )

    write_template(
        path.join(transforms, 'common', '__init__.py'),
        init + generate_all('entities')
    )

    write_template(
        path.join(transforms, 'common', 'entities.py'),
        read_template('entities', values)
    )


def help_():
    parser.print_help()


def description():
    return parser.description


def ask_user(defaults):
    print('Welcome to the Canari transform package wizard.')

    if not parse_bool('Would you like to specify authorship information? [Y/n]: '):
        return

    defaults['description'] = raw_input('Project description [%s]: ' % defaults['description']) or defaults[
        'description']
    defaults['example'] = parse_bool('Generate an example transform? [Y/n]: ')
    defaults['author'] = raw_input('Author name [%s]: ' % defaults['author']) or defaults['author']
    defaults['email'] = raw_input('Author email []: ') or ''
    defaults['maintainer'] = raw_input('Maintainer name [%s]: ' % defaults['author']) or defaults['author']

    if not parse_bool('Are you satisfied with this information? [Y/n]: '):
        return ask_user(defaults)


def run(args):
    opts = parser.parse_args(args)

    package_name = opts.package
    capitalized_package_name = package_name.capitalize()

    values = {
        'package': package_name,
        'entity': 'My%sEntity' % capitalized_package_name,
        'base_entity': '%sEntity' % capitalized_package_name,
        'project': capitalized_package_name,
        'author': getuser(),
        'year': datetime.now().year,
        'namespace': package_name,
        'email': '',
        'maintainer': getuser(),
        'example': True,
        'description': '',
        'canari_version': canari.__version__
    }

    ask_user(values)

    base = path.join(package_name, 'src', package_name)
    transforms = path.join(base, 'transforms')
    resources = path.join(base, 'resources')

    if not path.exists(package_name):
        print('creating skeleton in %s' % package_name)
        build_skeleton(
            package_name,
            [package_name, 'src'],
            [package_name, 'maltego'],
            base,
            transforms,
            [transforms, 'common'],
            resources,
            [resources, 'etc'],
            [resources, 'images'],
            [resources, 'external'],
            [resources, 'maltego']
        )
    else:
        print('A directory with the name %s already exists... exiting' % package_name)
        exit(-1)

    init = read_template('__init__', values)

    write_setup(package_name, values)

    write_root(base, init)

    write_resources(package_name, resources, init, values)

    write_common(transforms, init, values)

    print('done!')