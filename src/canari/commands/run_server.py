#!/usr/bin/env python

from ..maltego.message import (MaltegoTransformResponseMessage, MaltegoException,
                               MaltegoTransformExceptionMessage, MaltegoMessage, Message)
from common import cmd_name, import_transform, fix_binpath, fix_pypath
from ..config import config

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from xml.etree.cElementTree import fromstring
from os import execvp, geteuid, name, path
from SocketServer import ThreadingMixIn
from ssl import wrap_socket, CERT_NONE
from argparse import ArgumentParser
from cStringIO import StringIO
from urlparse import urlsplit
from sys import argv
from re import sub


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


parser = ArgumentParser(
    description='Runs a transform server for the given packages.',
    usage='canari %s <transform package> [...]' % cmd_name(__name__)
)

parser.add_argument(
    'packages',
    metavar='<package>',
    help='The name of the transform packages you wish to host (e.g. mypkg.transforms).',
    nargs='+'
)

parser.add_argument(
    '--port',
    metavar='<port>',
    default=-1,
    type=int,
    help='The port the server will run on.'
)

parser.add_argument(
    '--disable-ssl',
    action='store_true',
    default=False,
    help='Any extra parameters that can be sent to the local transform.'
)

parser.add_argument(
    '--enable-privileged',
    action='store_true',
    default=False,
    help='DANGEROUS: permit TDS to run packages that require elevated privileges.'
)

parser.add_argument(
    '--listen-on',
    metavar='[address]',
    default='',
    help='The address of the interface to listen on.'
)

parser.add_argument(
    '--cert',
    metavar='[certificate]',
    default='cert.pem',
    help='The name of the certificate file used for the server in PEM format.'
)


def help():
    parser.print_help()


def description():
    return parser.description


def message(m, r):
    """Write a MaltegoMessage to stdout and exit successfully"""

    r.send_response(200)
    r.send_header('Content-Type', 'text/xml')
    r.send_header('Connection', 'close')
    r.end_headers()

    sio = StringIO()
    m.entities
    Message(MaltegoMessage(m)).write(sio)
    v = sio.getvalue()
    # Get rid of those nasty unicode 32 characters
    r.wfile.write(sub(r'(&#\d{5};){2}', r'', v))


def croak(error_msg, r):
    """Throw an exception in the Maltego GUI containing error_msg."""

    r.send_response(200)
    r.send_header('Content-Type', 'text/xml')
    r.send_header('Connection', 'close')
    r.end_headers()

    Message(
        MaltegoMessage(
            MaltegoTransformExceptionMessage(exceptions=MaltegoException(error_msg)
            )
        )
    ).write(file=r.wfile)


class MaltegoTransformRequestHandler(BaseHTTPRequestHandler):

    protocol_version = 'HTTP/1.1'
    server_version = 'Canari/1.0'
    count = 0


    def dotransform(self, t):

        try:
            if 'Content-Length' not in self.headers:
                self.send_error(500, 'What?')
                return

            xml = fromstring(self.rfile.read(int(self.headers['Content-Length']))).find('MaltegoTransformRequestMessage')

            e = xml.find('Entities/Entity')
            etype = e.get('Type', '')

            if t[1] and etype not in t[1]:
                self.send_error(400, 'Unsupported input entity!')
                return

            value = e.find('Value').text or ''
            fields = dict([(f.get('Name', ''), f.text) for f in xml.findall('Entities/Entity/AdditionalFields/Field')])
            params = dict([(f.get('Name', ''), f.text) for f in xml.findall('TransformFields/Field')])
            limits = xml.find('Limits').attrib

            msg = t[0](
                type(
                    'MaltegoTransformRequestMessage',
                    (object,),
                        {
                        'value' : value,
                        'fields' : fields,
                        'params' : params,
                        'limits' : limits
                    }
                )(),
                MaltegoTransformResponseMessage()
            )


            if isinstance(msg, MaltegoTransformResponseMessage):
                message(msg, self)
                return
            elif isinstance(msg, basestring):
                raise MaltegoException(msg)
            else:
                raise MaltegoException('Could not resolve message type returned by transform.')

        except MaltegoException, me:
            croak(str(me), self)
        except Exception, e:
            croak(str(e), self)

    def do_POST(self):
        path = urlsplit(self.path or '/').path

        if path not in self.server.transforms:
            self.send_error(404, "Duh?")
        else:
            self.dotransform(self.server.transforms[path])

    def do_GET(self):
        self.count += 1
        print self.count
        path = urlsplit(self.path or '/').path
        if path in self.server.transforms:
            self.send_error(200, 'Yes')
            return
        self.send_error(404, 'No')


class SecureMaltegoHTTPServer(HTTPServer):

    def __init__(self, server_address=('', 8080), RequestHandlerClass=MaltegoTransformRequestHandler,
                 bind_and_activate=True, transforms={}, cert='cert.pem'):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.socket = wrap_socket(self.socket, server_side=True, certfile=cert, cert_reqs=CERT_NONE)
        self.transforms = transforms
        self.server_name = 'Canari'


class MaltegoHTTPServer(HTTPServer):

    def __init__(self, server_address=('', 8080), RequestHandlerClass=MaltegoTransformRequestHandler,
                 bind_and_activate=True, transforms={}):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.transforms = transforms


class AsyncSecureMaltegoHTTPServer(ThreadingMixIn, SecureMaltegoHTTPServer):
    pass


class AsyncMaltegoHTTPServer(ThreadingMixIn, MaltegoHTTPServer):
    pass



def run(args):

    opts = parser.parse_args(args)

    fix_pypath()

    if opts.port == -1:
        opts.port = 443 if not opts.disable_ssl else 80

    if name == 'posix' and geteuid() and (opts.port <= 1024 or opts.enable_privileged):
        print ('You must run this server as root to continue...')
        execvp('sudo', ['sudo'] + list(argv))

    fix_binpath(config['default/path'])


    transforms = {}

    print ('Loading transform packages...')

    try:
        for p in opts.packages:

            if not p.endswith('.transforms'):
                p = ('%s.transforms' % p)

            print ('Loading transform package %s' % p)

            m = __import__(p, globals(), locals(), ['*'])

            for t in m.__all__:

                t = ('%s.%s' % (p, t))
                m2 = import_transform(t)

                if not hasattr(m2, 'dotransform'):
                    continue

                if name == 'posix' and hasattr(m2.dotransform, 'privileged') and (geteuid() or not opts.enable_privileged):
                    continue

                if hasattr(m2.dotransform, 'remote') and m2.dotransform.remote:
                    print ('Loading %s at /%s...' % (t, t))
                    if hasattr(m2.dotransform, 'inputs'):
                        inputs = [e[1]('').type for e in m2.dotransform.inputs]
                        inputs = inputs + [i.split('.')[-1] for i in inputs]
                        transforms['/%s' % t] = (m2.dotransform, inputs)
                    else:
                        transforms['/%s' % t] = (m2.dotransform, [])

    except Exception, e:
        print (str(e))
        print ('Failed to load transforms... exiting')
        exit(-1)

    if not transforms:
        print ("Couldn't find any remote transforms... you sure you got this right?")
        exit(-1)

    httpd = None

    print ('Starting web server on %s:%s...' % (opts.listen_on, opts.port))
    server_address = (opts.listen_on, opts.port)

    if not opts.disable_ssl:
        if not path.exists(opts.cert):
            print ('The certificate file %s does not exist. Please create a PEM file...' % repr(opts.cert))
            exit(-1)
        print ('Making it secure (1337)...')
        httpd = AsyncSecureMaltegoHTTPServer(server_address=server_address, transforms=transforms, cert=opts.cert)
    else:
        print ('Really? Over regular HTTP? What a shame...')
        httpd = AsyncMaltegoHTTPServer(server_address=server_address, transforms=transforms)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()