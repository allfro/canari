#!/usr/bin/env python

from utils.stack import modulecallee

from imghdr import what
from pkg_resources import resource_filename, resource_listdir, resource_isdir

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


etc = 'canari.resources.etc'


def imageicon(pkg, name):
    name = resource_filename(pkg, name)
    if name[0] != '/':
        return 'file:///%s' % name
    return 'file://%s' % name


def imagepath(pkg, name):
    return '%s' % resource_filename(pkg, name)


def external_resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources.external' % modulecallee().__name__.split('.')[0]
    return resource_filename(pkg, name)


def image_resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources.images' % modulecallee().__name__.split('.')[0]
    return imagepath(pkg, name)


def icon_resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources.images' % modulecallee().__name__.split('.')[0]
    return imageicon(pkg, name)


def image_resources(pkg=None, dir='resources'):
    if pkg is None:
        pkg = modulecallee().__name__.split('.')[0]
    pkg_dir = '%s.%s' % (pkg, dir)
    images = []
    for i in resource_listdir(pkg, dir):
        fname = resource_filename(pkg_dir, i)
        if resource_isdir(pkg_dir, i):
            images.extend(image_resources(pkg_dir, i))
        elif what(fname) is not None:
            images.append(fname)
    return images

# etc
conf = resource_filename(etc, 'canari.conf')
