#!/usr/bin/env python

from common import console_message, cmd_name, highlight, fix_pypath, fix_binpath
from ..maltego.message import MaltegoTransformResponseMessage
from ..config import config

from code import InteractiveConsole
from argparse import ArgumentParser
from os import path, environ
from atexit import register
from re import sub, match
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


class MtgConsole(InteractiveConsole):

    def __init__(self, package):
        m = __import__(package, globals(), locals(), ['*'])
        m.__dict__[MaltegoTransformResponseMessage.__name__] = MaltegoTransformResponseMessage
        m.__dict__['message'] = console_message
        InteractiveConsole.__init__(self, locals=m.__dict__)
        self.init_history(path.expanduser('~/.mtgsh_history'))

    def raw_input(self, prompt):
        line = InteractiveConsole.raw_input(self, prompt=highlight('mtg> ', None, True))
        r = match(r'([^(]+)\((.*?)\)', line)
        if r is not None:
            g = r.groups()
            if g[0] in self.locals:
                line = eval(sub(r'([^\(]+)\((.*)\)', r'self.docall("\1", \2)', line))
        return line

    def docall(self, *args, **kwargs):
        return """message(%s.dotransform(
            type(
                'MaltegoTransformRequestMessage',
                (object,),
                {
                    'value' : %s,
                    'fields' : %s,
                    'params' : %s
                }
            )(),
            MaltegoTransformResponseMessage()
        ))""" % (args[0], repr(args[1]) if len(args) != 1 else repr(''), repr(kwargs), repr(args[2:]))

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
