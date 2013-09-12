#!/usr/bin/env python

# Builtin imports
from xml.etree.cElementTree import fromstring
from ConfigParser import NoSectionError
from cStringIO import StringIO
from urlparse import urljoin
import importlib
import hashlib
import sys
import os
import re

__version__ = '0.2'

# Third-party imports
from flask import Flask, Response, request

# Canari imports
import canari.config as _config
from canari.commands.common import get_transform_version
from canari.maltego.message import (Message, MaltegoMessage, MaltegoTransformRequestMessage,
                                    MaltegoTransformResponseMessage, MaltegoTransformExceptionMessage, MaltegoException)
from canari.resource import image_resources


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class Canari(Flask):
    def __init__(self, import_name):
        super(Canari, self).__init__(import_name)
        self.transforms = {}
        self._initialize()

    def _copy_images(self, pkg):
        if pkg.endswith('.transforms'):
            pkg = pkg.replace('.transforms', '')
        for i in image_resources(pkg):
            dname = 'static/%s' % hashlib.md5(i).hexdigest()
            if not os.path.exists(dname):
                with file(i, mode='rb') as src:
                    with open(dname, mode="wb") as dst:
                        dst.write(src.read())

    def _initialize(self):
        # Flask application container reload hack.
        reload(_config)

        packages = None

        # Read modules that are to be loaded at runtime
        try:
            packages = _config.config['remote/modules']
        except NoSectionError:
            sys.stderr.write('Exiting... You did not specify a [remote] section and a "modules" '
                             'option in your canari.conf file!')
            exit(-1)

        # Is packages not blank
        if not packages:
            sys.stderr.write('Exiting... You did not specify any transform modules to load in your canari.conf file!')
            exit(-1)
        elif isinstance(packages, basestring):
            packages = [packages]

        # Create the static directory for static file loading
        if not os.path.exists('static'):
            os.mkdir('static', 0755)

        # Iterate through the list of packages to load
        for p in packages:
            # Copy all the image resource files in case they are used as entity icons
            self._copy_images(p)

            if not p.endswith('.transforms'):
                p = ('%s.transforms' % p)

            sys.stderr.write('Loading transform package %s\n' % repr(p))

            # Load our first transform package
            m = importlib.import_module(p)

            for transform_name in m.__all__:
                transform_name = ('%s.%s' % (p, transform_name))

                # Let's import our transforms one by one
                transform_module = importlib.import_module(transform_name)
                if not hasattr(transform_module, 'dotransform'):
                    continue

                # Should the transform be publicly available?
                if hasattr(transform_module.dotransform, 'remote') and transform_module.dotransform.remote:
                    sys.stderr.write('Loading transform %s at /%s...\n' % (repr(transform_name), transform_name))
                    # Does it conform to V2 of the Canari transform signature standard?
                    if get_transform_version(transform_module.dotransform) == 2:
                        sys.stderr.write('ERROR: Plume does not support V2 Canari transforms (%s). Please update to V3.'
                                         ' See http://www.canariproject.com/4-3-transform-development-quick-start/ for'
                                         ' more details.\n' % repr(transform_name))
                        exit(-1)
                    # Does the transform need to be executed as root? If so, is this running in mod_wsgi? Yes = Bad!
                    elif os.name == 'posix' and hasattr(transform_module.dotransform, 'privileged') and \
                            os.geteuid() and __name__.startswith('_mod_wsgi_'):
                        sys.stderr.write('WARNING: mod_wsgi does not allow applications to run with root privileges. '
                                         'Transform %s ignored...\n' % repr(transform_name))
                        continue
                    # So everything is good, let's register our transform with the global transform registry.
                    inputs = {}
                    if hasattr(transform_module.dotransform, 'inputs'):
                        for category, entity_type in transform_module.dotransform.inputs:
                            inputs[entity_type.type] = entity_type
                            inputs[entity_type._v2type_] = entity_type
                    self.transforms[transform_name] = (transform_module.dotransform, inputs)


# Create our Flask app.
app = Canari(__name__)


def croak(error_msg):
    """Throw an exception in the Maltego GUI containing error_msg."""
    s = StringIO()
    Message(
        MaltegoMessage(
            MaltegoTransformExceptionMessage(exceptions=MaltegoException(error_msg))
        )
    ).write(file=s)
    return s.getvalue()


def message(m):
    """Write a MaltegoMessage to stdout and exit successfully"""
    v = None
    if isinstance(m, basestring):
        # Let's make sure that we're not spewing out local file system information ;)
        for url in re.findall("<iconurl>\s*(file://[^\s<]+)\s*</iconurl>(?im)", m):
            path = 'static/%s' % hashlib.md5(url[7:]).hexdigest()
            new_url = urljoin(request.host_url, path)
            m.replace(url, new_url, 1)
        v = m
    else:
        sio = StringIO()
        # Let's make sure that we're not spewing out local file system information ;)
        for e in m.entities:
            if e.iconurl is not None:
                e.iconurl = e.iconurl.strip()
                if e.iconurl.startswith('file://'):
                    path = 'static/%s' % hashlib.md5(e.iconurl[7:]).hexdigest()
                    new_url = urljoin(request.host_url, path)
                    e.iconurl = new_url

        Message(MaltegoMessage(m)).write(sio)
        v = sio.getvalue()
    # Get rid of those nasty unicode 32 characters
    return Response(re.sub(r'(&#\d{5};){2}', r'', v), status=200, mimetype='text/html')


def dotransform(transform, valid_input_entity_types):
    try:
        # Get the body of the request
        request_str = request.data

        # Let's get an XML object tree
        xml = fromstring(request_str).find('MaltegoTransformRequestMessage')

        # Get the entity being passed in.
        e = xml.find('Entities/Entity')
        entity_type = e.get('Type', '')

        if valid_input_entity_types and entity_type not in valid_input_entity_types:
            return Response(status=404)

        # Initialize Maltego Request values to pass into transform
        value = e.find('Value').text or ''
        fields = dict([(f.get('Name', ''), f.text) for f in xml.findall('Entities/Entity/AdditionalFields/Field')])
        params = dict([(f.get('Name', ''), f.text) for f in xml.findall('TransformFields/Field')])
        limits = xml.find('Limits').attrib

        # Initialize a private copy of the config to pass into the transform
        config = _config.CanariConfigParser()
        for k, i in params.items():
            if '.' in k:
                config[k.replace('.', '/', 1)] = i
            else:
                config['default/%s' % k] = i
        # The private config variables CANNOT override the server's settings. This is for security?
        config._sections.update(_config.config._sections)

        # Execute it!
        msg = transform(
            MaltegoTransformRequestMessage(value, fields, params, limits),
            request_str if hasattr(transform, 'cmd') and callable(transform.cmd) else MaltegoTransformResponseMessage(),
            config
        )

        # Let's serialize the return response and clean up whatever mess was left behind
        if isinstance(msg, MaltegoTransformResponseMessage) or isinstance(msg, basestring):
            return message(msg)
        else:
            raise MaltegoException('Could not resolve message type returned by transform.')

    # Unless we croaked somewhere, then we need to fix things up here...
    except MaltegoException, me:
        return croak(str(me))
    except Exception, e:
        return croak(str(e))


# This is where the TDS will ask: "Are you a transform?" and we say "200 - Yes I am!" or "404 - PFO"
@app.route('/<transform_name>', methods=['GET'])
def transform_checker(transform_name):
    if transform_name not in app.transforms:
        return Response(status=404)
    return Response(status=200)


# This is where we process a transform request.
@app.route('/<transform_name>', methods=['POST'])
def transform_runner(transform_name):
    if transform_name not in app.transforms:
        return Response(status=400)
    return dotransform(*app.transforms[transform_name])


# Finally, if you want to run Flask standalone for debugging, just type python plume.py and you're off to the races!
if __name__ == '__main__':
    app.run(debug=True)
