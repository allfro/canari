#!/usr/bin/env python

from canari.config import CanariConfigParser

from os import path, listdir, sep, environ, mkdir, pathsep, getcwd
from pkg_resources import resource_filename
from distutils.dist import Distribution
from distutils.command.install import install
from sys import path as pypath, platform
from datetime import datetime
from string import Template


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

def fix_etree():
    try:
        from xml.etree.cElementTree import XML
        e = XML('<test><t a="1"/></test>')
        e.find('t[@a="1"]')
    except SyntaxError:
        import canari.xmltools.fixetree

def get_bin_dir():
    d = install(Distribution())
    d.finalize_options()
    return d.install_scripts


def get_commands(module='canari.commands'):
    sc = __import__(module, globals(), locals(), fromlist=['__all__'])
    commands = {}
    for c in sc.__all__:
        m = __import__('%s.%s' % (module, c), globals(), locals(), fromlist=['run', 'help'])
        if 'run' in dir(m):
            commands[cmd_name(m.__name__)] = m
    return commands


def _detect_settings_dir(d):
    vs = [ i for i in listdir(d) if path.isdir(path.join(d, i)) if path.isdir(path.join(d, i, 'config'))]
    if len(vs) == 1:
        return path.join(d, vs[0])
    else:
        while True:
            print('Multiple versions of Maltego detected: ')
            for i, v in enumerate(vs):
                print('[%d] Maltego %s' % (i, v))
            r = raw_input('Please select which version you wish to use [0]: ')
            try:
                if not r:
                    return path.join(d, vs[0])
                elif int(r) < len(vs):
                    return path.join(d, vs[int(r)])
            except ValueError:
                pass
            print('Invalid selection... %s' % repr(r))
    print('Could not automatically find Maltego\'s settings directory. Use the -w parameter to specify its location, instead.')


def detect_settings_dir():
    d = None
    if platform.startswith('linux'):
        d = _detect_settings_dir(path.join(path.expanduser('~'), '.maltego'))
    elif platform == 'darwin':
        d = _detect_settings_dir(path.join(path.expanduser('~'), 'Library', 'Application Support', 'maltego'))
    elif platform == 'win32':
        d = _detect_settings_dir(path.join(environ['APPDATA'], '.maltego'))
    else:
        raise NotImplementedError('Unknown or unsupported OS: %s' % repr(platform))
    return d


def read_template(name, values):
    t = Template(file(resource_filename('canari.resources.template', '%s.plate' % name)).read())
    return t.substitute(**values)


def write_template(fname, data):
    print('creating file %s...' % fname)
    with file(fname, mode='wb') as w:
        w.write(data)


def generate_all(*args):
    return "\n__all__ = [\n    '%s'\n]" % "',\n    '".join(args)


def build_skeleton(*args):
    for d in args:
        if isinstance(d, list):
            d = sep.join(d)
        print('creating directory %s' % d)
        mkdir(d)


def highlight(string, color, bold):
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
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)


def croak(exc):
    print(highlight(exc, 'red', None))


def fix_pypath():
    if '' not in pypath:
        pypath.insert(0, '')


def fix_binpath(paths):
    if paths is not None:
        if isinstance(paths, basestring):
            environ['PATH'] = paths
        elif isinstance(paths, list):
            environ['PATH'] = pathsep.join(paths)


def import_transform(script):
    fix_pypath()
    return __import__(script, globals(), locals(), ['dotransform'])


def import_package(package):
    fix_pypath()
    return __import__(package, globals(), locals(), ['*'])


def cmd_name(name):
    return name.replace('canari.commands.', '').replace('_', '-')


def console_message(msg, tab=-1):
    tab += 1
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
    tab -= 1


def init_pkg():

    conf = '.canari'

    for i in range(0, 5):
        if path.exists(conf):
            c = CanariConfigParser()
            c.read(conf)
            return {
                'author' : c['metadata/author'],
                'email' : c['metadata/email'],
                'maintainer' : c['metadata/maintainer'],
                'project' : c['metadata/project'],
                'year' : datetime.now().year,
                'dir' : getcwd()
            }
        conf = '..%s%s' % (sep, conf)

    return {
        'author' : '',
        'email' : '',
        'maintainer' : '',
        'project' : '',
        'year' : datetime.now().year
    }



