#!/usr/bin/env python

from common import get_commands, cmd_name

from argparse import ArgumentParser
from sys import modules


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

cmds = get_commands()
cmds.update({'help': modules[__name__]})

parser = ArgumentParser(
    description='Shows help related to various canari commands',
    usage='canari %s <command>' % cmd_name(__name__)
)

parser.add_argument(
    'command',
    metavar='<command>',
    choices=cmds,
    default='help',
    nargs='?',
    help='The canari command you want help for (%s)' % ', '.join(cmds)
)


def help_():
    parser.print_help()


def description():
    return parser.description


def run(args):
    cmds[parser.parse_args(args).command].help_()