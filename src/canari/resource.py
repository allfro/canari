#!/usr/bin/env python

from pkg_resources import resource_filename


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Sploitego Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


etc = 'canari.resources.etc'


def imageicon(pkg, name):
    return 'file://%s' % resource_filename(pkg, name)


def imagepath(pkg, name):
    return '%s' % resource_filename(pkg, name)


# etc
conf = resource_filename(etc, 'canari.conf')