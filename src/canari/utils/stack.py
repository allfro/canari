#!/usr/bin/env python

from inspect import stack, getmodule

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'modulecallee'
]

def modulecallee(atframe=2):
    frame = stack()[atframe]
    return getmodule(frame[0])