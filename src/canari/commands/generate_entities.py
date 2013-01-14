#!/usr/bin/env python

from common import detect_settings_dir, cmd_name, project_tree, parse_bool
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
__version__ = '0.1'
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


def help():
    parser.print_help()


def description():
    return parser.description


def parse_args(args):
    args = parser.parse_args(args)
    if args.outfile is None:
        args.outfile = path.join(project_tree()['transforms'], 'common', 'entities.py')
    return args


def normalize_fn(fn):
        # Get rid of starting underscores or numbers and bad chars for var names in python
        return sub(r'[^A-Za-z0-9]', '', sub(r'^[^A-Za-z]+', '', fn))


def diff(fn):
    m = load_source('entities', fn)
    l = []
    for c in dir(m):
        try:
            i = m.__dict__[c]('load')
            if isinstance(i, Entity):
                l.append(i)
        except TypeError:
            pass
    return l


class DirFile(object):

    def __init__(self, path):
        self.path = path

    def namelist(self):
        l = []
        for base, dirs, files in walk(self.path):
            l.extend([ path.join(base, f) for f in files ])
        return l

    def open(self, fname):
        return file(fname)


def run(args):

    opts = parse_args(args)

    if path.exists(opts.outfile) and not opts.append and not \
       parse_bool('%s already exists. Are you sure you want to overwrite it? [y/N]: ' % repr(opts.outfile), default='n'):
        exit(-1)


    ar = DirFile(
        path.join(detect_settings_dir(), 'config', 'Maltego', 'Entities')
    ) if opts.mtz_file is None else ZipFile(opts.mtz_file)

    entities = filter(lambda x: x.endswith('.entity'), ar.namelist())

    nses = dict()

    el = []
    if opts.append:
        l = diff(opts.outfile)
        el.extend([i.type for i in l])
        for i in l:
            if i.type.endswith('Entity'):
                nses[i.namespace] = i.__class__.__name__

    print 'Generating %s...' % repr(opts.outfile)
    fd = open(opts.outfile, 'ab' if opts.append else 'wb')

    if opts.append:
        fd.write('\n\n')
    else:
        fd.write('#!/usr/bin/env python\n\nfrom canari.maltego.entities import EntityField, Entity\n\n\n')

    for e in entities:
        xml = XML(ar.open(e).read())
        id_ = xml.get('id')

        if (opts.entity and id_ not in opts.entity) or id_ in el:
            continue

        ens = id_.split('.')

        base_classname = None
        namespace = '.'.join(ens[:-1])
        name = ens[-1]
        classname = name

        if (opts.namespace and namespace not in opts.namespace) or namespace in opts.exclude_namespace:
            continue

        if namespace not in nses:
            base_classname = '%sEntity' % (''.join([ n.title() for n in ens[:-1] ]))
            nses[namespace] = base_classname

            fd.write('class %s(Entity):\n    namespace = %s\n\n' % (base_classname, repr(namespace)))
        else:
            base_classname = nses[namespace]


        for f in xml.findall('Properties/Fields/Field'):
            fields = [
                'name=%s' % repr(f.get('name')),
                'propname=%s' % repr(normalize_fn(f.get('name'))),
                'displayname=%s' % repr(f.get('displayName'))

            ]
            fd.write('@EntityField(%s)\n' % ', '.join(fields))

        fd.write('class %s(%s):\n    pass\n\n\n' % (classname, base_classname))

    fd.close()
    print 'done.'