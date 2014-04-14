#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')

import canari

scripts = [
    'src/scripts/canari',
    'src/scripts/dispatcher',
]

if os.name == 'posix':
    scripts.extend(
        [
            'src/scripts/pysudo'
        ]
    )

extras = [
    'readline'
]

requires = [
    'argparse',
    'flask',
    'Twisted',
    'safedexml'
]

if os.name == 'nt':
    scripts += ['%s.bat' % s for s in scripts]

setup(
    name='canari',
    author='Nadeem Douba',
    version=canari.__version__,
    author_email='ndouba@gmail.com',
    description='Rapid transform development and transform execution framework for Maltego.',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=scripts,
    zip_safe=False,
    package_data={
        '': ['*.conf', '*.plate']
    },
    install_requires=requires,
    dependency_links=[]
)
