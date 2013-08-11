#!/usr/bin/env python

from canari.resource import external_resource
from canari.utils.stack import calling_package

from subprocess import PIPE, Popen
import os
import re


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'privileged',
    'specification'
]


def superuser(f):
    f.privileged = True
    return f


def deprecated(f):
    f.deprecated = True
    return f


class configure(object):
    def __init__(self, **kwargs):
        diff = set(['label', 'uuids', 'inputs']).difference(kwargs)
        if diff:
            raise TypeError('Missing transform specification properties: %s' % ', '.join(diff))
        if not isinstance(kwargs['uuids'], list):
            raise TypeError('Expected type list (got %s instead)' % type(kwargs['uuids']).__name__)
        if not isinstance(kwargs['inputs'], list):
            raise TypeError('Expected type list (got %s instead)' % type(kwargs['inputs']))
        kwargs['description'] = kwargs.get('description', '')
        kwargs['debug'] = kwargs.get('debug', False)
        self.function = kwargs.get('cmd', None)
        self.specification = kwargs

    def __call__(self, f):
        if callable(self.function):
            self.function.__dict__.update(f.__dict__)
            f = self.function
        f.__dict__.update(self.specification)
        return f


class ExternalCommand(object):
    def __init__(self, transform_name, transform_args=None, interpreter=None, is_resource=True):
        if transform_args is None:
            transform_args = []
        self._extra_external_args = []

        if interpreter is not None:
            self._extra_external_args.append(interpreter)
            libpath = external_resource(
                os.path.dirname(transform_name),
                '%s.resources.external' % calling_package()
            )
            if interpreter.startswith('perl') or interpreter.startswith('ruby'):
                self._extra_external_args.extend(['-I', libpath])
            elif interpreter.startswith('java'):
                self._extra_external_args.extend(['-cp', libpath])

        if ' ' in transform_name:
            raise ValueError('Transform name %s cannot have spaces.' % repr(transform_name))
        elif not is_resource:
            self._extra_external_args.append(transform_name)
        else:
            self._extra_external_args.append(
                external_resource(
                    transform_name,
                    '%s.resources.external' % calling_package()
                )
            )

        if isinstance(transform_args, basestring):
            self._extra_external_args = re.split(r'\s+', transform_args)
        else:
            self._extra_external_args.extend(transform_args)

    def __call__(self, request, request_xml):
        args = [request.value]
        if isinstance(request.params, list) and request.params:
            args.extend(request.params)
        if request.fields:
            args.append('#'.join(['%s=%s' % (k, v) for k, v in request.fields.iteritems()]))
        if isinstance(request_xml, basestring):
            p = Popen(self._extra_external_args + list(args), stdin=PIPE, stdout=PIPE)
            out, err = p.communicate(request_xml)
            return out
        p = Popen(self._extra_external_args + list(args))
        p.communicate()
        exit(p.returncode)
