#!/usr/bin/env python

from common import cmd_name

from csv import reader, DictWriter
from argparse import ArgumentParser


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Convert mixed entity type CSVs to separated CSV sheets.',
    usage='canari %s <graph csv> [sheet prefix]' % cmd_name(__name__)
)

parser.add_argument(
    'graph',
    metavar='<graph csv>',
    help='The CSV file containing the output from the mtgx2csv command.'
)

parser.add_argument(
    'prefix',
    metavar='[sheet prefix]',
    nargs='?',
    help='The prefix to prepend to the generated CSV files.'
)


def help_():
    parser.print_help()


def description():
    return parser.description


def parse_args(args):
    return parser.parse_args(args)


def run(args):

    opts = parse_args(args)
    opts.prefix = opts.prefix or opts.graph.split('.', 1)[0]

    sheets = {}
    sheet_headers = {}

    try:
        with file(opts.graph) as csvfile:
            for row in reader(csvfile):
                fv = dict(column.split('=', 1) for column in row)
                entity_type = fv.pop('Entity Type')
                headers = fv.keys()
                if entity_type not in sheets:
                    sheets[entity_type] = [fv]
                    sheet_headers[entity_type] = set(headers)
                    continue
                else:
                    sheets[entity_type].append(fv)
                if len(headers) > len(sheet_headers[entity_type]):
                    sheet_headers[entity_type].union(headers)

        for entity_type in sheets:
            with open('%s_%s.csv' % (opts.prefix, entity_type), 'wb') as csvfile:
                csv = DictWriter(csvfile, sheet_headers[entity_type])
                csv.writeheader()
                csv.writerows(sheets[entity_type])
    except IOError, e:
        print 'csv2sheets: %s' % e
        exit(-1)