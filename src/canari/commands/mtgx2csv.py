#!/usr/bin/env python

from common import cmd_name, to_utf8

from xml.etree.cElementTree import XML
from argparse import ArgumentParser
from zipfile import ZipFile


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Convert Maltego graph files (*.mtgx) to comma-separated values (CSV) file.',
    usage='canari %s <graph>' % cmd_name(__name__)
)

parser.add_argument(
    'graph',
    metavar='<graph>',
    help='The name of the graph file you wish to convert to CSV.',
)


def parse_args(args):
    return parser.parse_args(args)


def help():
    parser.print_help()


def description():
    return parser.description


def run(args):

    opts = parse_args(args)

    zip = ZipFile(opts.graph)
    graphs = filter(lambda x: x.endswith('.graphml'), zip.namelist())

    for f in graphs:
        csv = open(f.split('/')[1].split('.')[0] + '.csv', 'w')
        xml = XML(zip.open(f).read())
        for e in xml.findall('{http://graphml.graphdrawing.org/xmlns}graph/{http://graphml.graphdrawing.org/xmlns}node/{http://graphml.graphdrawing.org/xmlns}data/{http://maltego.paterva.com/xml/mtgx}MaltegoEntity'):
            csv.write(to_utf8(('"Entity Type=%s",' % e.get('type')).strip()))
            for prop in e.findall('{http://maltego.paterva.com/xml/mtgx}Properties/{http://maltego.paterva.com/xml/mtgx}Property'):
                value = prop.find('{http://maltego.paterva.com/xml/mtgx}Value').text or ''
                if '"' in value:
                    value.replace('"', '""')
                csv.write(to_utf8(('"%s=%s",' % (prop.get('displayName'), value)).strip().replace('\n', ', ')))
            csv.write('\n')