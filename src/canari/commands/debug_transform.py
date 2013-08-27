#!/usr/bin/env python

import os
import sys

from argparse import ArgumentParser
from traceback import format_exc

from common import croak, import_transform, cmd_name, console_message, fix_binpath, sudo, get_transform_version
from canari.maltego.message import (MaltegoException, MaltegoTransformResponseMessage, UIMessage,
                                    MaltegoTransformRequestMessage)
from canari.maltego.utils import onterminate, parseargs
from canari.config import config


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Runs Canari local transforms in a terminal-friendly fashion.',
    usage='canari %s <transform> [param1 ... paramN] <value> [field1=value1...#fieldN=valueN]' % cmd_name(__name__)
)

parser.add_argument(
    'transform',
    metavar='<transform>',
    help='The name of the transform you wish to run (e.g. sploitego.transforms.nmapfastscan).'
)

parser.add_argument(
    'value',
    metavar='<value>',
    help='The value of the input entity being passed into the local transform.'
)

parser.add_argument(
    'params',
    metavar='[param1 ... paramN]',
    help='Any extra parameters that can be sent to the local transform.'
)

parser.add_argument(
    'fields',
    metavar='[field1=value1...#fieldN=valueN]',
    help='The fields of the input entity being passed into the local transform.'
)


def help_():
    parser.print_help()


def description():
    return parser.description


def run(args):

    [transform, params, value, fields] = parseargs(['canari %s' % cmd_name(__name__)] + args)

    m = None
    fix_binpath(config['default/path'])
    try:
        m = import_transform(transform)

        if os.name == 'posix' and hasattr(m.dotransform, 'privileged') and os.geteuid():
            rc = sudo(sys.argv)
            if rc == 1:
                console_message(MaltegoTransformResponseMessage() + UIMessage('User cancelled transform.'))
            elif rc == 2:
                console_message(MaltegoTransformResponseMessage() + UIMessage('Too many incorrect password attempts.'))
            elif rc:
                console_message(MaltegoTransformResponseMessage() + UIMessage('Unknown error occurred.'))
            exit(rc)

        if hasattr(m, 'onterminate'):
            onterminate(m.onterminate)
        else:
            m.__setattr__('onterminate', lambda *args: exit(-1))

        msg = m.dotransform(
            MaltegoTransformRequestMessage(value, fields, params),
            MaltegoTransformResponseMessage()
        ) if get_transform_version(m.dotransform) == 2 else m.dotransform(
            MaltegoTransformRequestMessage(value, fields, params),
            MaltegoTransformResponseMessage(),
            config
        )

        if isinstance(msg, MaltegoTransformResponseMessage):
            console_message(msg)
        elif isinstance(msg, basestring):
            raise MaltegoException(msg)
        else:
            raise MaltegoException('Could not resolve message type returned by transform.')
    except MaltegoException, me:
        croak(str(me))
    except ImportError:
        e = format_exc()
        croak(e)
    except Exception:
        e = format_exc()
        croak(e)
    except KeyboardInterrupt, ki:
        if m is not None:
            m.onterminate()