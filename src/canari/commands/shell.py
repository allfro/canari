#!/usr/bin/env python

import os
import sys

from code import InteractiveConsole
from argparse import ArgumentParser
from atexit import register

from common import console_message, cmd_name, highlight, fix_pypath, fix_binpath, import_package
from canari.maltego.message import MaltegoTransformResponseMessage
from canari.config import config


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Creates a Canari debug shell for the specified transform package.',
    usage='canari %s <package name>' % cmd_name(__name__)
)

parser.add_argument(
    'package',
    metavar='<package name>',
    help='The name of the canari package you wish to load local transform from for the Canari shell session.'
)


def help_():
    parser.print_help()


def description():
    return parser.description


class ShellCommand(object):

    def __init__(self, mod):
        self.mod = mod
        self.sudoargs = ['sudo'] + list(sys.argv)

    def __call__(self, value, *args, **kwargs):
        if os.name == 'posix' and hasattr(self.mod.dotransform, 'privileged') and os.geteuid():
            print highlight("Need to be root to run this transform... sudo'ing...", 'green', True)
            os.execvp('sudo', self.sudoargs)
            return
        return console_message(self.mod.dotransform(
            type(
                'MaltegoTransformRequestMessage',
                (object,),
                    {
                    'value' : value,
                    'params' : list(args),
                    'fields' : kwargs
                }
            )(),
            MaltegoTransformResponseMessage()
        ))


class MtgConsole(InteractiveConsole):

    def __init__(self, package):
        package = import_package(package)
        transforms = dict(dir=dir)
        for name, mod in package.__dict__.iteritems():
            if getattr(mod, 'dotransform', ''):
                transforms[name] = ShellCommand(mod)
        InteractiveConsole.__init__(self, locals=transforms)
        self.init_history(os.path.expanduser('~/.mtgsh_history'))

    def init_history(self, histfile):
        try:
            import readline
            readline.parse_and_bind('tab: complete')
            if hasattr(readline, "read_history_file"):
                try:
                    readline.read_history_file(histfile)
                except IOError:
                    pass
                register(lambda h: readline.write_history_file(h), histfile)
        except ImportError:
            pass


def run(args):

    opts = parser.parse_args(args)

    fix_binpath(config['default/path'])
    fix_pypath()

    if not opts.package.endswith('transforms'):
        opts.package = '%s.transforms' % opts.package

    mtgsh = MtgConsole(opts.package)
    mtgsh.interact(highlight('Welcome to Canari.', 'green', True))
