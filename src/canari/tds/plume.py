#!/usr/bin/env python

# Builtin imports
from ConfigParser import NoSectionError
import traceback
from urlparse import urljoin
import hashlib
import sys
import os
import re

# Third-party imports
from canari.pkgutils.transform import TransformDistribution
from flask import Flask, Response, request

# Canari imports
import canari.config as _config
from canari.maltego.utils import get_transform_version
from canari.maltego.message import (MaltegoMessage, MaltegoTransformResponseMessage, MaltegoTransformExceptionMessage,
                                    MaltegoException)

# Monkey patch our resource lib to automatically rewrite icon urls
import canari.resource
imgres = canari.resource.image_resource
canari.resource.image_resource = \
    lambda name, pkg=None: '%sstatic/%s' % (request.host_url, hashlib.md5(imgres(name, pkg)).hexdigest())
canari.resource.icon_resource = canari.resource.image_resource
callpkg = canari.resource.calling_package
canari.resource.calling_package = lambda frame=4: callpkg(frame)

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.4'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class Canari(Flask):

    four_o_four = 'Whaaaaat?'

    def __init__(self, import_name):
        super(Canari, self).__init__(import_name)
        self.transforms = {}
        self.resources = []
        self._initialize()

    def _copy_images(self, pkg):
        if pkg.endswith('.transforms'):
            pkg = pkg.replace('.transforms', '')
        for i in canari.resource.image_resources(pkg):
            dname = 'static/%s' % hashlib.md5(i).hexdigest()
            self.resources.append(dname)
            if not os.path.exists(dname):
                print 'Copying %s to %s...' % (i, dname)
                with open(i, mode='rb') as src:
                    with open(dname, mode="wb") as dst:
                        dst.write(src.read())

    def _initialize(self):
        # Flask application container reload hack.
        reload(_config)

        packages = None

        # Read packages that are to be loaded at runtime
        try:
            packages = _config.config['remote/packages']
        except NoSectionError:
            sys.stderr.write('Exiting... You did not specify a [remote] section and a "packages" '
                             'option in your canari.conf file!\n')
            exit(-1)

        # Is packages not blank
        if not packages:
            sys.stderr.write('Exiting... You did not specify any transform packages to load in your canari.conf file!\n')
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

            distribution = TransformDistribution(p)

            sys.stderr.write('Loading transform package %s\n' % repr(p))

            for transform in distribution.remote_transforms:
                transform_name = transform.__name__
                sys.stderr.write('Loading transform %s at /%s...\n' % (repr(transform_name), transform_name))
                # Should the transform be publicly available?
                # Does it conform to V2 of the Canari transform signature standard?
                if get_transform_version(transform.dotransform) == 2:
                    sys.stderr.write('ERROR: Plume does not support V2 Canari transforms (%s). Please update to V3.'
                                     ' See http://www.canariproject.com/4-3-transform-development-quick-start/ for'
                                     ' more details.\n' % repr(transform_name))
                    exit(-1)
                    # Does the transform need to be executed as root? If so, is this running in mod_wsgi? Yes = Bad!
                elif os.name == 'posix' and hasattr(transform.dotransform, 'privileged') and \
                        os.geteuid() and __name__.startswith('_mod_wsgi_'):
                    sys.stderr.write('WARNING: mod_wsgi does not allow applications to run with root privileges. '
                                     'Transform %s ignored...\n' % repr(transform_name))
                    continue

                # So everything is good, let's register our transform with the global transform registry.
                inputs = {}
                if hasattr(transform.dotransform, 'inputs'):
                    for category, entity_type in transform.dotransform.inputs:
                        inputs[entity_type._type_] = entity_type
                        inputs[entity_type._v2type_] = entity_type
                self.transforms[transform_name] = (transform.dotransform, inputs)


# Create our Flask app.
app = Canari(__name__)


def croak(error_msg):
    """Throw an exception in the Maltego GUI containing error_msg."""
    return MaltegoMessage(
        message=MaltegoTransformExceptionMessage(
            exceptions=[
                MaltegoException(error_msg)
            ]
        )
    ).render()


def message(m):
    """Write a MaltegoMessage to stdout and exit successfully"""
    v = None
    if isinstance(m, str):
        # Let's make sure that we're not spewing out local file system information ;)
        for url in re.findall("<iconurl>\s*(file://[^\s<]+)\s*</iconurl>(?im)", m):
            path = 'static/%s' % hashlib.md5(url[7:]).hexdigest()
            new_url = urljoin(request.host_url, path)
            m.replace(url, new_url, 1)
        v = m
    else:
        v = MaltegoMessage(message=m).render()
    return Response(v, status=200, mimetype='text/html')


def dotransform(transform, valid_input_entity_types):
    try:
        # Get the body of the request
        request_str = request.data

        # Let's get an XML object tree
        maltego_request = MaltegoMessage.parse(request_str).message

        # Get the entity being passed in.
        e = maltego_request.entity
        entity_type = e.type

        if valid_input_entity_types and entity_type not in valid_input_entity_types:
            return Response(app.four_o_four, status=404)

        # Initialize a private copy of the config to pass into the transform
        config = _config.CanariConfigParser()
        for p in maltego_request.parameters.values():
            if '.' in p.name:
                config[p.name.replace('.', '/', 1)] = p.value
            else:
                config['plume/%s' % p.name] = p.value
        # The private config variables CANNOT override the server's settings. This is for security?
        config._sections.update(_config.config._sections)

        # Execute it!
        msg = transform(
            maltego_request,
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
        return croak(traceback.format_exc())


# This is where the TDS will ask: "Are you a transform?" and we say "200 - Yes I am!" or "404 - PFO"
@app.route('/<transform_name>', methods=['GET'])
def transform_checker(transform_name):
    if transform_name in app.transforms:
        return Response('Yes?', status=200)
    return Response(app.four_o_four, status=404)

@app.route('/static/<resource_name>', methods=['GET'])
def static_fetcher(resource_name):
    resource_name = 'static/%s' % resource_name
    if resource_name in app.resources:
        return Response(file(resource_name, mode='rb').read(), status=200, mimetype='application/octet-stream')
    return Response(app.four_o_four, status=404)


# This is where we process a transform request.
@app.route('/<transform_name>', methods=['POST'])
def transform_runner(transform_name):
    if transform_name not in app.transforms:
        return Response(app.four_o_four, status=404)
    return dotransform(*app.transforms[transform_name])


# Finally, if you want to run Flask standalone for debugging, just type python plume.py and you're off to the races!
if __name__ == '__main__':
    app.run(debug=True)
