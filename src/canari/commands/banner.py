#!/usr/bin/env python

from common import canari_main
from framework import SubCommand


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.3'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


@SubCommand(
    canari_main,
    help='Show banner of Canari framework that is currently active.',
    description='Show banner of Canari framework that is currently active.'
)
def banner(args):
    print """
    Your running ...
        dBBBP dBBBBBb     dBBBBb dBBBBBb   dBBBBBb    dBP    dBBBb   dBBBb
                   BB        dBP      BB       dBP
      dBP      dBP BB   dBP dBP   dBP BB   dBBBBK   dBP       dBP     dBP
     dBP      dBP  BB  dBP dBP   dBP  BB  dBP  BB  dBP       dBP     dBP
    dBBBBP   dBBBBBBB dBP dBP   dBBBBBBB dBP  dB' dBP       dBP dBP dBP
                                            ... http://canariproject.com
    """