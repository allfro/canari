#!/usr/bin/env python

from common import detect_settings_dir, cmd_name, project_tree, parse_bool, maltego_version
from canari.maltego.entities import Entity

from xml.etree.cElementTree import XML
from argparse import ArgumentParser
from os import walk, path
from zipfile import ZipFile
from imp import load_source
from re import sub


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = ['Nadeem Douba']

__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

parser = ArgumentParser(
    description='Converts Maltego entity definition files to Canari python classes. Excludes Maltego built-in entities.',
    usage='canari %s [output file] [options]' % cmd_name(__name__)
)

parser.add_argument(
    'outfile',
    metavar='[output file]',
    help='Which file to write the output to.',
    default=None,
    nargs='?'
)

parser.add_argument(
    '--mtz-file',
    '-m',
    metavar='<mtzfile>',
    help='A *.mtz file containing an export of Maltego entities.',
    required=False
)

parser.add_argument(
    '--exclude-namespace',
    '-e',
    metavar='<namespace>',
    help='Name of Maltego entity namespace to ignore. Can be defined multiple times.',
    required=False,
    action='append',
    default=['maltego', 'maltego.affiliation']
)

parser.add_argument(
    '--namespace',
    '-n',
    metavar='<namespace>',
    help='Name of Maltego entity namespace to generate entity classes for. Can be defined multiple times.',
    required=False,
    action='append',
    default=[]
)

parser.add_argument(
    '--maltego-entities',
    '-M',
    help="Generate entities belonging to the 'maltego' namespace.",
    default=False,
    action='store_true'
)

parser.add_argument(
    '--append',
    '-a',
    help='Whether or not to append to the existing *.py file.',
    action='store_true',
    default=False
)

parser.add_argument(
    '--entity',
    '-E',
    metavar='<entity>',
    help='Name of Maltego entity to generate Canari python class for.',
    required=False,
    action='append',
    default=[]
)


def help_():
    parser.print_help()


def description():
    return parser.description


def parse_args(args):
    args = parser.parse_args(args)
    if args.outfile is None:
        args.outfile = path.join(project_tree()['transforms'], 'common', 'entities.py')
    if args.maltego_entities:
        args.namespace.extend(args.exclude_namespace)
        args.exclude_namespace = []
    return args


def normalize_fn(fn):
    # Get rid of starting underscores or numbers and bad chars for var names in python
    return sub(r'[^A-Za-z0-9]', '', sub(r'^[^A-Za-z]+', '', fn))


def get_existing_entities(filename):
    m = load_source('entities', filename)
    l = []
    for c in dir(m):
        try:
            entity_class = m.__dict__[c]
            if issubclass(entity_class, Entity):
                l.append(entity_class)
        except TypeError:
            pass
    return l


class DirFile(object):
    def __init__(self, path):
        self.path = path

    def namelist(self):
        l = []
        for base, dirs, files in walk(self.path):
            l.extend([path.join(base, f) for f in files])
        return l

    def open(self, fname):
        return file(fname)


def run(args):
    opts = parse_args(args)

    if path.exists(opts.outfile) and not opts.append and not \
        parse_bool('%s already exists. Are you sure you want to overwrite it? [y/N]: ' % repr(opts.outfile),
                   default='n'):
        exit(-1)

    entity_source = None
    if opts.mtz_file is None:
        d = detect_settings_dir()
        if maltego_version(d) >= '3.4.0':
            print("""
=========================== ERROR: NOT SUPPORTED ===========================

 Starting from Maltego v3.4.0 the 'canari generate-entities' command can no
 longer generate entity definition files from the Maltego configuration
 directory. Entities can only be generated from export files (*.mtz). To
 export entities navigate to the 'Manage' tab in Maltego, then click on the
 'Export Entities' button and follow the prompts. Once the entities have
 been exported, run the following command:

 shell> canari generate-entities -m myentities.mtz

=========================== ERROR: NOT SUPPORTED ===========================
                """)
            exit(-1)
        entity_source = DirFile(
            path.join(d, 'config', 'Maltego', 'Entities')
        )
    else:
        entity_source = ZipFile(opts.mtz_file)

    entity_files = filter(lambda x: x.endswith('.entity'), entity_source.namelist())

    namespaces = dict()

    excluded_entities = []
    if opts.append:
        existing_entities = get_existing_entities(opts.outfile)
        # excluded_entities.extend([e._type_ for e in existing_entities])
        for entity_class in existing_entities:
            excluded_entities.extend(entity_class._type_)
            if entity_class._type_.endswith('Entity'):
                namespaces[entity_class._namespace_] = entity_class.__name__

    print 'Generating %s...' % repr(opts.outfile)
    outfile = open(opts.outfile, 'ab' if opts.append else 'wb')

    if opts.append:
        outfile.write('\n\n')
    else:
        outfile.write('#!/usr/bin/env python\n\nfrom canari.maltego.entities import EntityField, Entity\n\n\n')

    for entity_file in entity_files:
        xml = XML(entity_source.open(entity_file).read())
        id_ = xml.get('id')

        if (opts.entity and id_ not in opts.entity) or id_ in excluded_entities:
            continue

        namespace_entity = id_.split('.')

        base_classname = None
        namespace = '.'.join(namespace_entity[:-1])
        name = namespace_entity[-1]
        classname = name

        if (opts.namespace and namespace not in opts.namespace) or namespace in opts.exclude_namespace:
            continue

        if namespace not in namespaces:
            base_classname = '%sEntity' % (''.join([n.title() for n in namespace_entity[:-1]]))
            namespaces[namespace] = base_classname

            outfile.write('class %s(Entity):\n    _namespace_ = %s\n\n' % (base_classname, repr(namespace)))
        else:
            base_classname = namespaces[namespace]

        for field in xml.findall('Properties/Fields/Field'):
            fields = [
                'name=%s' % repr(field.get('name')),
                'propname=%s' % repr(normalize_fn(field.get('name'))),
                'displayname=%s' % repr(field.get('displayName'))

            ]
            outfile.write('@EntityField(%s)\n' % ', '.join(fields))

        outfile.write('class %s(%s):\n    pass\n\n\n' % (classname, base_classname))

    outfile.close()
    print 'done.'