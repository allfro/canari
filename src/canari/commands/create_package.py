#!/usr/bin/env python

from datetime import datetime
from getpass import getuser
from os import path

from common import read_template, write_template, generate_all, build_skeleton, canari_main, parse_bool, parse_str
from framework import SubCommand, Argument
import canari


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.8'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


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
    if values['create_example']:
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


def ask_user(defaults):
    print('Welcome to the Canari transform package wizard.')

    while True:
        if not parse_bool('Would you like to specify authorship information?', defaults['create_authorship']):
            return

        defaults['description'] = parse_str('Project description', defaults['description'])
        defaults['create_example'] = parse_bool('Generate an example transform?', defaults['create_example'])
        defaults['author'] = parse_str('Author name', defaults['author'])
        defaults['email'] = parse_str('Author email', defaults['email'])
        defaults['maintainer'] = parse_str('Maintainer name', defaults['author'])

        if parse_bool('Are you satisfied with this information?'):
            return


@SubCommand(
    canari_main,
    help='Creates a Canari transform package skeleton.',
    description='Creates a Canari transform package skeleton.'
)
@Argument(
    'package',
    metavar='<package name>',
    help='The name of the canari package you wish to create.'
)
def create_package(opts):

    package_name = opts.package
    capitalized_package_name = package_name.capitalize()

    values = {
        'package': package_name,
        'entity': 'My%sEntity' % capitalized_package_name,
        'base_entity': '%sEntity' % capitalized_package_name,
        'project': capitalized_package_name,
        'create_authorship': True,
        'author': getuser(),
        'year': datetime.now().year,
        'namespace': package_name,
        'email': '',
        'maintainer': getuser(),
        'create_example': True,
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