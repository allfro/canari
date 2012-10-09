#!/usr/bin/env python

from os import name #, path, system, symlink, pathsep
#from distutils.sysconfig import get_config_var
from setuptools import setup, find_packages
#from subprocess import PIPE, Popen
#from sys import argv


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


#if 'fixpath' not in argv:
setup(
    name='canari',
    author='Nadeem Douba',
    version='0.1',
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


# Fixing Canari script path to work with JVM
#elif 'fixpath' in argv:
#    print '\nChecking PATH of JVM and Canari...'
#
#    if not path.exists('java/JVMPathChecker.class') and system('javac java/JVMPathChecker.java'):
#        print 'Error compiling the path checker using javac.'
#        exit(-1)
#
#    proc = Popen(['java', '-cp', 'java', 'JVMPathChecker'], stdout=PIPE)
#    jvm_path = proc.communicate()[0][:-1].split(pathsep)
#
#    bindir = get_config_var('BINDIR')
#
#    if bindir not in jvm_path:
#        print "Warning %s not in your JVM's PATH" % bindir
#
#        while True:
#            i = 0
#            for i, path_dir in enumerate(jvm_path):
#                print '[%d]: %s' % (i, path_dir)
#
#            try:
#                selection = int(
#                    raw_input("Please select the path where you'd like to place symlinks to Canari's scripts [0]: ")
#                )
#                if selection <= i:
#                    for script in scripts:
#                        srcf = path.join(bindir, script)
#                        dstf = path.join(jvm_path[selection], script)
#                        if not path.exists(srcf):
#                            print 'Could not find %s in %s' % (repr(script), repr(bindir))
#                            exit(-1)
#                        elif path.exists(dstf):
#                            print 'skipping %s since it already exists in %s...' % (
#                                repr(script),
#                                repr(jvm_path[selection])
#                                )
#                            continue
#                        print 'symlinking %s to %s...' % (srcf, dstf)
#                        symlink(srcf, dstf)
#                    exit(0)
#                raise ValueError
#            except ValueError:
#                print 'Invalid selection... try again.'
#    else:
#        print 'All looks good... no further action required here.'
#
#
#
#print '\nChecking if other dependencies installed...'
#
#for e in extras:
#    try:
#        __import__(e)
#    except ImportError:
#        print 'WARNING: Package %s not installed. Please download and manually install this package' % repr(e)
