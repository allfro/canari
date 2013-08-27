#!/usr/bin/env python

from common import get_commands, cmd_name
from argparse import ArgumentParser
from sys import modules

import canari


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Show version of Canari framework that is currently active.',
    usage='canari %s' % cmd_name(__name__)
)


def help_():
    parser.print_help()


def description():
    return parser.description


def run(args):
    print 'Your running *Canari Framework v%s*' % canari.__version__