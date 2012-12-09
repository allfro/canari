#!/usr/bin/env python

from setuptools import setup, find_packages
from os import name


scripts = [
    'src/scripts/canari',
    'src/scripts/pysudo',
    'src/scripts/dispatcher',
]

extras = [
    'readline'
]

if name == 'nt':
    scripts += ['%s.bat' % s for s in scripts]


setup(
    name='canari',
    author='Nadeem Douba',
    version='0.4',
    author_email='ndouba@gmail.com',
    description='Rapid transform development and transform execution framework for Maltego.',
    license='GPL',
    packages=find_packages('src'),
    package_dir={ '' : 'src' },
    scripts=scripts,
    zip_safe=False,
    package_data={
        '' : [ '*.conf', '*.plate' ]
    },
    install_requires=[
        'pexpect',
        'argparse'
    ],
    dependency_links=[]
)