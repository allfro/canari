#!/usr/bin/env python

import inspect
import signal
import sys
import os
import traceback
from types import ModuleType
from xml.etree.cElementTree import fromstring
from safedexml import Model

from canari.commands.common import sudo, import_transform
from canari.maltego.entities import Unknown
from message import MaltegoMessage, MaltegoTransformExceptionMessage, MaltegoException, \
    MaltegoTransformResponseMessage, MaltegoTransformRequestMessage, UIMessage, Field

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'onterminate',
    'message',
    'highlight',
    'console_message',
    'croak',
    'guess_entity_type',
    'to_entity',
    'get_transform_version',
    'local_transform_runner',
    'debug',
    'progress'
]


def onterminate(func):
    """Register a signal handler to execute when Maltego forcibly terminates the transform."""
    signal.signal(signal.SIGTERM, func)
    signal.signal(signal.SIGINT, func)


def message(m, fd=sys.stdout):
    """Write a MaltegoMessage to stdout and exit successfully"""
    print MaltegoMessage(message=m).render(fragment=True)
    sys.exit(0)


def highlight(s, color, bold):
    """
    Internal API: Returns the colorized version of the text to be returned to a POSIX terminal. Not compatible with
    Windows (yet).
    """
    if os.name == 'posix':
        attr = []
        if color == 'green':
            # green
            attr.append('32')
        elif color == 'red':
            # red
            attr.append('31')
        else:
            attr.append('30')
        if bold:
            attr.append('1')
        s = '\x1b[%sm%s\x1b[0m' % (';'.join(attr), s)

    return s


def console_message(msg, tab=-1):
    """
    Internal API: Returns a prettified tree-based output of an XML message for debugging purposes. This helper function
    is used by the debug-transform command.
    """
    tab += 1

    if isinstance(msg, Model):
        msg = fromstring(msg.render(fragment=True))

    print('%s`- %s: %s %s' % (
        '  ' * tab,
        highlight(msg.tag, None, True),
        highlight(msg.text, 'red', False) if msg.text is not None else '',
        highlight(msg.attrib, 'green', True) if msg.attrib.keys() else ''
    ))
    for c in msg.getchildren():
        print('  %s`- %s: %s %s' % (
            '  ' * tab,
            highlight(c.tag, None, True),
            highlight(c.text, 'red', False) if c.text is not None else '',
            highlight(c.attrib, 'green', True) if c.attrib.keys() else ''
        ))
        for sc in c.getchildren():
            tab += 1
            console_message(sc, tab)
            tab -= 1


def croak(error_msg, message_writer=message):
    """Throw an exception in the Maltego GUI containing error_msg."""
    message_writer(MaltegoTransformExceptionMessage(exceptions=[MaltegoException(error_msg)]))


def guess_entity_type(transform_module, fields):
    """
    Internal API: Returns the entity type based on the following best match algorithm:

    1. If a transform does not specify the input entity types, the Unknown entity will be returned.
    2. If a transform only has one input entity type, then that entity type will be returned.
    3. If a transform has more than one input entity type, then the entity type that has the
       most number of matching entity fields in the entity's class definition will be returned.

    This is only used by the local transform runner to detect the input entity type since this information is excluded
    at run-time.
    """
    if not hasattr(transform_module.dotransform, 'inputs') or not transform_module.dotransform.inputs:
        return Unknown
    if len(transform_module.dotransform.inputs) == 1 or not fields:
        return transform_module.dotransform.inputs[0][1]
    num_matches = 0
    best_match = Unknown
    for category, entity_type in transform_module.dotransform.inputs:
        l = len(set(entity_type._fields_to_properties_.keys()).intersection(fields.keys()))
        if l > num_matches:
            num_matches = l
            best_match = entity_type
    return best_match


def to_entity(entity_type, value, fields):
    """
    Internal API: Returns an instance of an entity of type entity_type with the specified value and fields (stored in
    dict). This is only used by the local transform runner as a helper function.
    """
    e = entity_type(value)
    for k, v in fields.iteritems():
        e.fields[k] = Field(k, v)
    return e


def get_transform_version(transform):
    """
    Internal API: Returns the version of the transform function based on the transform function's signature. Currently,
    only two versions are supported (2 and 3). This is what version 2 transform functions look like:

    def transform(request, response):
        ...

    Version 3 transforms have the additional config variable like so:

    def transform(request, response, config):
        ...

    Or can have a varargs parameter as a third argument:

    def transform(request, response, *args):
        ...

    In both cases, version 3 transforms will be passed a local copy of the canari configuration object as the third
    argument. However, in the latter example, the configuration object will be stored in a tuple (i.e. (config,)).
    """
    spec = inspect.getargspec(transform)
    if spec.varargs is not None:
        return 3
    n = len(spec.args)
    if 2 <= n <= 3:
        return n
    raise Exception('Could not determine transform version.')


def local_transform_runner(transform, value, fields, params, config, message_writer=message):
    """
    Internal API: The local transform runner is responsible for executing the local transform.

    Parameters:

    transform      - The name or module of the transform to execute (i.e sploitego.transforms.whatismyip).
    value          - The input entity value.
    fields         - A dict of the field names and their respective values.
    params         - The extra parameters passed into the transform via the command line.
    config         - The Canari configuration object.
    message_writer - The message writing function used to write the MaltegoTransformResponseMessage to stdout. This is
                     can either be the console_message or message functions. Alternatively, the message_writer function
                     can be any callable object that accepts the MaltegoTransformResponseMessage as the first parameter
                     and writes the output to a destination of your choosing.

    This helper function is only used by the run-transform, debug-transform, and dispatcher commands.
    """
    transform_module = None
    try:
        transform_module = transform if isinstance(transform, ModuleType) else import_transform(transform)

        if os.name == 'posix' and hasattr(transform_module.dotransform, 'privileged') and os.geteuid():
            rc = sudo(sys.argv)
            if rc == 1:
                message_writer(MaltegoTransformResponseMessage() + UIMessage('User cancelled transform.'))
            elif rc == 2:
                message_writer(MaltegoTransformResponseMessage() + UIMessage('Too many incorrect password attempts.'))
            elif rc:
                message_writer(MaltegoTransformResponseMessage() + UIMessage('Unknown error occurred.'))
            sys.exit(rc)

        if hasattr(transform_module, 'onterminate'):
            onterminate(transform_module.onterminate)
        else:
            transform_module.__setattr__('onterminate', lambda *args: sys.exit(-1))

        input_entity = to_entity(guess_entity_type(transform_module, fields), value, fields)

        msg = transform_module.dotransform(
            MaltegoTransformRequestMessage(
                entities=[input_entity.__entity__],
                parameters={'canari.local.arguments': Field(name='canari.local.arguments', value=params)}
            ),
            MaltegoTransformResponseMessage()
        ) if get_transform_version(transform_module.dotransform) == 2 else transform_module.dotransform(
            MaltegoTransformRequestMessage(
                entities=[input_entity.__entity__],
                parameters={'canari.local.arguments': Field(name='canari.local.arguments', value=params)}
            ),
            MaltegoTransformResponseMessage(),
            config
        )
        if isinstance(msg, MaltegoTransformResponseMessage):
            message_writer(msg)
        elif isinstance(msg, basestring):
            raise MaltegoException(msg)
        else:
            raise MaltegoException('Could not resolve message type returned by transform.')
    except MaltegoException, me:
        croak(str(me), message_writer)
    except ImportError:
        e = traceback.format_exc()
        croak(e, message_writer)
    except Exception:
        e = traceback.format_exc()
        croak(e, message_writer)
    except KeyboardInterrupt:
        if transform_module:
            transform_module.onterminate()


def debug(*args):
    """Send debug messages to the Maltego console."""
    for i in args:
        sys.stderr.write('D:%s\n' % str(i))
        sys.stderr.flush()


def progress(i):
    """Send a progress report to the Maltego console."""
    sys.stderr.write('%%%d\n' % min(max(i, 0), 100))
    sys.stderr.flush()