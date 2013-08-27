#!/usr/bin/env python

from common import cmd_name, to_utf8

from csv import writer
from xml.etree.cElementTree import XML
from argparse import ArgumentParser
from zipfile import ZipFile


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.4'
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


def help_():
    parser.print_help()


def description():
    return parser.description


def run(args):
    opts = parse_args(args)

    zipfile = ZipFile(opts.graph)
    graphs = filter(lambda x: x.endswith('.graphml'), zipfile.namelist())

    for f in graphs:
        with open(f.split('/')[1].split('.')[0] + '.csv', 'wb') as csvfile:
            csv = writer(csvfile)
            xml = XML(zipfile.open(f).read())
            links = {}
            for edge in xml.findall('{http://graphml.graphdrawing.org/xmlns}graph/'
                                    '{http://graphml.graphdrawing.org/xmlns}edge'):
                src = edge.get('source')
                dst = edge.get('target')
                if src not in links:
                    links[src] = dict(in_=0, out=0)
                if dst not in links:
                    links[dst] = dict(in_=0, out=0)
                links[src]['out'] += 1
                links[dst]['in_'] += 1

            for node in xml.findall('{http://graphml.graphdrawing.org/xmlns}graph/'
                                    '{http://graphml.graphdrawing.org/xmlns}node'):

                node_id = node.get('id')
                node = node.find('{http://graphml.graphdrawing.org/xmlns}data/'
                                 '{http://maltego.paterva.com/xml/mtgx}MaltegoEntity')

                row = [to_utf8(('Entity Type=%s' % node.get('type')).strip())]
                for prop in node.findall('{http://maltego.paterva.com/xml/mtgx}Properties/'
                                         '{http://maltego.paterva.com/xml/mtgx}Property'):
                    value = prop.find('{http://maltego.paterva.com/xml/mtgx}Value').text or ''
                    row.append(to_utf8(('%s=%s' % (prop.get('displayName'), value)).strip()))
                row.append('Incoming Links=%s' % links[node_id]['in_'])
                row.append('Outgoing Links=%s' % links[node_id]['out'])
                csv.writerow(row)