#!/usr/bin/env python

from imghdr import what
from utils.stack import calling_package
from pkg_resources import resource_filename, resource_listdir, resource_isdir, resource_exists

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'external_resource',
    'image_resource',
    'icon_resource',
    'image_resources',
    'resource',
    'conf'
]


etc = 'canari.resources.etc'


def imageicon(pkg, name):
    name = resource_filename(pkg, name)
    if name[0] != '/':
        return 'file:///%s' % name
    return 'file://%s' % name


def imagepath(pkg, name):
    return resource_filename(pkg, name)


def external_resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources.external' % calling_package()
    return resource_filename(pkg, name)


def image_resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources.images' % calling_package()
    return imagepath(pkg, name)


def icon_resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources.images' % calling_package()
    return imageicon(pkg, name)


def image_resources(pkg=None, directory='resources'):
    if pkg is None:
        pkg = calling_package()
    pkg_dir = '%s.%s' % (pkg, directory)
    images = []
    for i in resource_listdir(pkg, directory):
        fname = resource_filename(pkg_dir, i)
        if resource_isdir(pkg_dir, i):
            images.extend(image_resources(pkg_dir, i))
        elif what(fname) is not None:
            images.append(fname)
    return images


def resource(name, pkg=None):
    if pkg is None:
        pkg = '%s.resources' % calling_package()
    resource = resource_filename(pkg, name)
    if not resource_exists(resource):
        raise OSError('Resource does not exist %s' % repr(resource))
    return resource

# etc
conf = resource_filename(etc, 'canari.conf')
