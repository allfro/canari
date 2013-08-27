#!/usr/bin/env python

from common import get_commands, cmd_name, highlight

from argparse import ArgumentParser
from sys import modules

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.6'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

cmds = get_commands()
cmds.update({'list-commands': modules[__name__]})

parser = ArgumentParser(
    description='Lists all the available canari commands.',
    usage='canari %s' % cmd_name(__name__)
)


def help_():
    parser.print_help()


def description():
    return parser.description


def run(args):
    k = cmds.keys()
    k.sort()
    for i in k:
        print ('%s - %s' % (highlight(i, 'green', True), cmds[i].description()))