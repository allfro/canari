#!/usr/bin/env python

from common import get_commands, cmd_name
from argparse import ArgumentParser
from sys import modules

import canari


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Show banner of Canari framework that is currently active.',
    usage='canari %s' % cmd_name(__name__)
)


def help():
    parser.print_help()


def description():
    return parser.description


def run(args):
    print """
    Your running ...
_________                           _____          _______  _______
__  ____/_____ _____________ __________(_)  ___   ___  __ \ __( __ )
_  /    _  __ `/_  __ \  __ `/_  ___/_  /   __ | / /  / / / _  __  |
/ /___  / /_/ /_  / / / /_/ /_  /   _  /    __ |/ // /_/ /__/ /_/ /
\____/  \__,_/ /_/ /_/\__,_/ /_/    /_/     _____/ \____/_(_)____/

                                ... http://canariproject.com
                                                                        """