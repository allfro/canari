#!/usr/bin/env python

import os
import sys
from code import InteractiveConsole
from atexit import register
from canari.pkgutils.transform import TransformDistribution

from common import canari_main, fix_pypath, fix_binpath, import_package, pushd
from framework import SubCommand, Argument
from canari.config import config
from canari.maltego.utils import highlight, console_message, local_transform_runner
import canari


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class ShellCommand(object):

    def __init__(self, mod):
        self.mod = mod
        self.sudoargs = ['sudo'] + list(sys.argv)

    def __call__(self, value, *args, **kwargs):
        if os.name == 'posix' and hasattr(self.mod.dotransform, 'privileged') and os.geteuid():
            print highlight("Need to be root to run this transform... sudo'ing...", 'green', True)
            os.execvp('sudo', self.sudoargs)
            return

        local_transform_runner(self.mod, value, kwargs, list(args), config, message_writer=console_message)


class MtgConsole(InteractiveConsole):

    def __init__(self, package):
        package = import_package(package)
        transforms = dict(dir=dir)
        for name, mod in package.__dict__.iteritems():
            if getattr(mod, 'dotransform', ''):
                transforms[name] = ShellCommand(mod)
        InteractiveConsole.__init__(self, locals=transforms)
        self.init_history(os.path.expanduser('~/.mtgsh_history'))

    def init_history(self, history_file):
        try:
            import readline
            readline.parse_and_bind('tab: complete')
            if hasattr(readline, "read_history_file"):
                try:
                    readline.read_history_file(history_file)
                except IOError:
                    pass
                register(lambda h: readline.write_history_file(h), history_file)
        except ImportError:
            pass


@SubCommand(
    canari_main,
    help='Creates a Canari debug shell for the specified transform package.',
    description='Creates a Canari debug shell for the specified transform package.'
)
@Argument(
    'package',
    metavar='<package name>',
    help='The name of the canari package you wish to load local transform from for the Canari shell session.'
)
@Argument(
    '-w',
    '--working-dir',
    metavar='[working dir]',
    default=None,
    help="the path that will be used as the working directory for "
         "the transforms being executed in the shell (default: ~/.canari/)"
)
def shell(opts):

    fix_binpath(config['default/path'])
    fix_pypath()

    if not opts.package.endswith('transforms'):
        opts.package = '%s.transforms' % opts.package

    try:
        t = TransformDistribution(opts.package)
        with pushd(opts.working_dir or t.default_prefix):
            mtg_console = MtgConsole(opts.package)
            mtg_console.interact(highlight('Welcome to Canari %s.' % canari.__version__, 'green', True))
    except ValueError, e:
        print str(e)
        exit(-1)
