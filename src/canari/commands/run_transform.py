#!/usr/bin/env python

import os
import sys
from traceback import format_exc

from argparse import ArgumentParser

from canari.maltego.message import (MaltegoException, MaltegoTransformResponseMessage, UIMessage,
                                    MaltegoTransformRequestMessage)
from canari.maltego.utils import onterminate, parseargs, croak, message
from common import cmd_name, import_transform, fix_binpath, sudo, get_transform_version, guess_entity_type, to_entity
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

    transform_module = None

    fix_binpath(config['default/path'])
    try:
        transform_module = import_transform(transform)

        if os.name == 'posix' and hasattr(transform_module.dotransform, 'privileged') and os.geteuid():
            rc = sudo(sys.argv)
            if rc == 1:
                message(MaltegoTransformResponseMessage() + UIMessage('User cancelled transform.'))
            elif rc == 2:
                message(MaltegoTransformResponseMessage() + UIMessage('Too many incorrect password attempts.'))
            elif rc:
                message(MaltegoTransformResponseMessage() + UIMessage('Unknown error occurred.'))
            exit(0)

        if hasattr(transform_module, 'onterminate'):
            onterminate(transform_module.onterminate)
        else:
            transform_module.__setattr__('onterminate', lambda *args: exit(-1))

        input_entity = to_entity(guess_entity_type(transform_module, fields), value, fields)

        msg = transform_module.dotransform(
            MaltegoTransformRequestMessage(value, fields, params, input_entity),
            MaltegoTransformResponseMessage()
        ) if get_transform_version(transform_module.dotransform) == 2 else transform_module.dotransform(
            MaltegoTransformRequestMessage(value, fields, params, input_entity),
            MaltegoTransformResponseMessage(),
            config
        )

        if isinstance(msg, MaltegoTransformResponseMessage):
            message(msg)
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
    except KeyboardInterrupt:
        if transform_module is not None:
            transform_module.onterminate()