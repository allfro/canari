#!/usr/bin/env python

from common import console_message, cmd_name, highlight, fix_pypath, fix_binpath, import_package
from ..maltego.message import MaltegoTransformResponseMessage
from ..config import config

from os import path, name, geteuid, execvp
from code import InteractiveConsole
from argparse import ArgumentParser
from atexit import register
from sys import argv
import readline


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
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


def help():
    parser.print_help()


def description():
    return parser.description


class ShellCommand(object):

    def __init__(self, mod):
        self.mod = mod
        self.sudoargs = ['sudo'] + list(argv)

    def __call__(self, value, *args, **kwargs):
        if name == 'posix' and hasattr(self.mod.dotransform, 'privileged') and geteuid():
            print highlight("Need to be root to run this transform... sudo'ing...", 'green', True)
            execvp('sudo', self.sudoargs)
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
        self.init_history(path.expanduser('~/.mtgsh_history'))

    def init_history(self, histfile):
        readline.parse_and_bind('tab: complete')
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)
        print ('bye!')


def run(args):

    opts = parser.parse_args(args)

    fix_binpath(config['default/path'])
    fix_pypath()

    if not opts.package.endswith('transforms'):
        opts.package = '%s.transforms' % opts.package

    mtgsh = MtgConsole(opts.package)
    mtgsh.interact(highlight('Welcome to Canari.', 'green', True))
