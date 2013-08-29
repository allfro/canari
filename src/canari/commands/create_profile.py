#!/usr/bin/env python

import os
import sys

from pkg_resources import resource_filename, resource_listdir
from xml.etree.cElementTree import XML, SubElement
from argparse import ArgumentParser
from re import findall, sub
from zipfile import ZipFile
from string import Template
from cStringIO import StringIO

from canari.maltego.configuration import (MaltegoTransform, CmdCwdTransformProperty, CmdDbgTransformProperty,
                                          CmdLineTransformProperty, CmdParmTransformProperty, InputConstraint,
                                          Set, TransformSettings, CmdCwdTransformPropertySetting,
                                          CmdDbgTransformPropertySetting, CmdLineTransformPropertySetting,
                                          CmdParmTransformPropertySetting, TransformSet, Transform, MaltegoServer, Authentication, Protocol)
from common import detect_settings_dir, cmd_name, fix_pypath, get_bin_dir, import_transform, import_package, fix_etree
from canari.maltego.message import ElementTree


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.2'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


# Dictionary of detected transforms
transforms = {}
transformsets = {}

# Argument parser
parser = ArgumentParser(
    description="Creates an importable Maltego profile (*.mtz) file.",
    usage='canari %s <package> [options]' % cmd_name(__name__)
)

parser.add_argument(
    'package',
    metavar='<package>',
    help='the name of the canari transforms package to install.'
)

parser.add_argument(
    '-w',
    '--working-dir',
    metavar='[working dir]',
    default=os.path.join(os.path.expanduser('~'), '.canari'),
    help='the path that will be used as the working directory for the transforms being installed (default: current working directory)'
)

# Help for this command
def help():
    parser.print_help()


def description():
    return parser.description


# Extra sauce to parse args
def parse_args(args):
    args = parser.parse_args(args)
    args.working_dir = os.path.realpath(args.working_dir)
    return args


def write_sets(profile):
    setsdir = 'TransformSets'

    s = StringIO()
    for set_, transforms in transformsets.iteritems():
        sets = TransformSet(set_)
        for t in transforms:
            sets += Transform(t)
        print ('Writing transform set %s to %s...' % (set_, profile.filename))
        s.truncate(0)
        ElementTree(sets).write(s)
        profile.writestr('/'.join([setsdir, '%s.set' % set_]), s.getvalue())


def write_server(profile):
    s = StringIO()
    server = MaltegoServer()
    server += Protocol()
    server += Authentication()
    for t in transforms:
        transform = Transform(t)
        server += transform
    ElementTree(server).write(s)
    print('Writing server Local to %s' % profile.filename)
    profile.writestr('Servers/Local.tas', s.getvalue())


# Logic to install transforms
def write_transform(module, name, author, spec, profile, working_dir):
    installdir = 'TransformRepositories/Local'

    s = StringIO()

    for i, n in enumerate(spec.uuids):

        if n in transforms:
            sys.stderr.write('WARNING: Previous declaration of %s in transform %s. Overwriting...' % (n, module))
        else:
            print ('Writing transform %s to %s...' % (n, profile.filename))
            transforms[n] = module

        intype = spec.inputs[i][1]._type_

        sets = None
        if spec.inputs[i][0] is not None:
            transformset = spec.inputs[i][0]
            if transformset not in transformsets:
                transformsets[transformset] = []
            transformsets[transformset].append(n)
            sets = Set(transformset)

        transform = MaltegoTransform(
            n,
            spec.label,
            author=author,
            description=spec.description,
            properties=[
                CmdLineTransformProperty(),
                CmdCwdTransformProperty(),
                CmdDbgTransformProperty(),
                CmdParmTransformProperty()
            ],
            input=InputConstraint(intype),
            sets=sets
        )
        transform.sets

        s.truncate(0)
        ElementTree(transform).write(s)
        profile.writestr('/'.join([installdir, '%s.transform' % n]), s.getvalue())


        transformsettings = TransformSettings(properties=[
            CmdLineTransformPropertySetting(
                os.path.join(get_bin_dir(),
                             'dispatcher.bat' if os.name == 'nt' else 'dispatcher')
            ),
            CmdParmTransformPropertySetting(name),
            CmdCwdTransformPropertySetting(working_dir),
            CmdDbgTransformPropertySetting(spec.debug)
        ])

        s.truncate(0)
        ElementTree(transformsettings).write(s)
        profile.writestr('/'.join([installdir, '%s.transformsettings' % n]), s.getvalue())


def writeconf(sf, df, **kwargs):
    if not os.path.exists(df):
        print ('Writing %s to %s' % (sf, df))
        with file(df, mode='wb') as w:
            if 'sub' in kwargs and kwargs['sub']:
                del kwargs['sub']
                w.write(
                    Template(
                        file(
                            sf
                        ).read()
                    ).substitute(**kwargs)
                )
            else:
                w.write(
                    file(
                        sf
                    ).read()
                )


def updateconf(c, f):
    ld = os.getcwd()
    os.chdir(os.path.dirname(f))

    import canari.config as config

    reload(config)

    if c not in config.config['default/configs']:
        print ('Updating %s...' % f)
        s = ''
        with file(f) as r:
            s = r.read()
        with file(f, mode='wb') as w:
            w.write(sub(r'configs\s*\=', 'configs = %s,' % c, s))
    os.chdir(ld)


def installconf(opts, args):
    src = resource_filename('canari.resources.template', 'canari.plate')
    writeconf(
        src,
        os.path.join(opts.working_dir, 'canari.conf'),
        sub=True,
        command=' '.join(['canari install'] + args),
        config=('%s.conf' % opts.package) if opts.package != 'canari' else '',
        path='${PATH},/usr/local/bin,/opt/local/bin' if os.name == 'posix' else ''
    )

    if opts.package != 'canari':
        src = resource_filename('%s.resources.etc' % opts.package, '%s.conf' % opts.package)
        writeconf(src, os.path.join(opts.working_dir, '%s.conf' % opts.package), sub=False)
        updateconf('%s.conf' % opts.package, os.path.join(opts.working_dir, 'canari.conf'))


def write_entities(package, profile):
    try:
        src = resource_filename('%s.resources.maltego' % package, 'entities.mtz')
        if not os.path.exists(src):
            return

        z = ZipFile(src)
        entities = filter(lambda x: x.endswith('.entity') or x.endswith('.category'), z.namelist())

        for e in entities:
            print ('Writing %s to %s...' % (e, profile.filename))
            profile.writestr(e, z.open(e).read())

    except ImportError:
        pass


def write_machines(package, profile):
    machinedir = 'Machines'
    package = '%s.resources.maltego' % package
    for m in filter(lambda x: x.endswith('.machine'), resource_listdir(package, '')):
        src = resource_filename(package, m)
        print 'Writing machine %s to %s...' % (src, profile.filename)
        profile.write(src, '/'.join([machinedir, m]))
        profile.writestr('/'.join([machinedir, m.replace('.machine', '.properties')]), 'enabled=true')


def makedirs(working_dir):
    name = ''
    if os.name != 'nt':
        name = os.sep
    for l, i in enumerate(working_dir.split(os.sep)):
        name = os.path.join(name, i)
        if name.endswith(':') and not l and os.name == 'nt':
            name = '%s%s' % (name, os.sep)
        if not os.path.exists(name):
            os.mkdir(name, 0755)


# Main
def run(args):
    if os.name == 'posix' and not os.geteuid():
        login = os.getlogin()

        if login != 'root':
            print 'Why are you using root to run this command? You should be using %s! Bringing you down...' % login
            import pwd

            user = pwd.getpwnam(login)
            os.setgid(user.pw_gid)
            os.setuid(user.pw_uid)

    opts = parse_args(args)

    makedirs(opts.working_dir)
    fix_pypath()
    fix_etree()

    if opts.package.endswith('.transforms'):
        opts.package = opts.package.replace('.transforms', '')

    try:
        print('Writing canari.config to %s...' % opts.working_dir)
        installconf(opts, args)
    except ImportError:
        pass

    print ('Looking for transforms in %s.transforms' % opts.package)
    m = None
    try:
        m = import_package('%s.transforms' % opts.package)
    except ImportError, e:
        print (
            "Does not appear to be a valid canari package. "
            "Couldn't import the '%s.transforms' package in '%s'. Error message: %s" % (
                opts.package, opts.package, e))
        exit(-1)

    print('Creating profile %s.mtz...' % opts.package)
    zf = ZipFile('%s.mtz' % opts.package, 'w')
    for t in m.__all__:
        transform = '%s.transforms.%s' % (opts.package, t)

        m2 = import_transform(transform)
        if hasattr(m2, 'dotransform') and hasattr(m2.dotransform, 'label'):
            write_transform(
                m2.__name__,
                transform,
                getattr(m2, '__author__', ''),
                m2.dotransform,
                zf,
                opts.working_dir
            )

    write_sets(zf)
    write_server(zf)

    write_entities(opts.package, zf)
    write_machines(opts.package, zf)

    zf.close()

    if not transforms:
        os.unlink(zf.filename)
        print ('Error: no transforms found...')
        exit(-1)
    else:
        print("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SUCCESS! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

 Successfully created %s. You may now import this file into
 Maltego.

 INSTRUCTIONS:
 -------------
 1. Open Maltego.
 2. Click on the home button (Maltego icon, top-left corner).
 3. Click on 'Import'.
 4. Click on 'Import Configuration'.
 5. Follow prompts.
 6. Enjoy!

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SUCCESS! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        """ % zf.filename)
