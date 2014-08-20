#!/usr/bin/env python

import os

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'highlight',
]


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
