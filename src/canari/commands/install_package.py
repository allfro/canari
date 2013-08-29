#!/usr/bin/env python

import os
import sys

from pkg_resources import resource_filename, resource_listdir
from xml.etree.cElementTree import XML, SubElement
from argparse import ArgumentParser
from re import findall, sub
from zipfile import ZipFile
from string import Template

from canari.maltego.configuration import  (MaltegoTransform, CmdCwdTransformProperty, CmdDbgTransformProperty,
                               CmdLineTransformProperty, CmdParmTransformProperty, InputConstraint, Set,
                               TransformSettings, CmdCwdTransformPropertySetting, CmdDbgTransformPropertySetting,
                               CmdLineTransformPropertySetting, CmdParmTransformPropertySetting)
from common import detect_settings_dir, cmd_name, fix_pypath, get_bin_dir, import_transform, import_package, fix_etree, maltego_version
from canari.maltego.message import ElementTree


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.5'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


# Dictionary of detected transforms
transforms = {}

# Argument parser
parser = ArgumentParser(
    description="Installs and configures canari transform packages in Maltego's UI",
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
parser.add_argument(
    '-s',
    '--settings-dir',
    metavar='[settings dir]',
    default=detect_settings_dir,
    help='the path to the Maltego settings directory (automatically detected if excluded)'
)


# Help for this command
def help_():
    parser.print_help()


def description():
    return parser.description


# Extra sauce to parse args
def parse_args(args):
    args = parser.parse_args(args)

    if args.settings_dir is detect_settings_dir:
        try:
            args.settings_dir = detect_settings_dir()
        except OSError:
            print "Make sure you've run Maltego for the first time and activated your license."
            exit(-1)

    if maltego_version(args.settings_dir) >= '3.4.0':
        print("""
=========================== ERROR: NOT SUPPORTED ===========================

 Starting from Maltego v3.4.0 the 'canari install-package' command is no
 longer supported. Please use the 'canari create-profile' command, instead.
 This will create an importable config file (*.mtz) which can be imported
 using the 'Import Configuration' option in Maltego. This option can be
 found by clicking on the <Maltego icon> in the top left corner of your
 Maltego window then scrolling to 'Import' then 'Import Configuration'.

 NOTE: This command will automatically install and configure the
 'canari.conf' file for you in the default location for your OS.

 EXAMPLE:

 shell> canari create-profile sploitego
 ...
 shell> ls
 sploitego.mtz <--- Import this file

=========================== ERROR: NOT SUPPORTED ===========================
        """)
        exit(-1)

    args.working_dir = os.path.realpath(args.working_dir)
    return args


# Logic to install transforms
def install_transform(module, name, author, spec, prefix, working_dir):

    installdir = os.path.join(prefix, 'config', 'Maltego', 'TransformRepositories', 'Local')

    if not os.path.exists(installdir):
        os.mkdir(installdir)

    setsdir = os.path.join(prefix, 'config', 'Maltego', 'TransformSets')

    for i, n in enumerate(spec.uuids):

        if n in transforms:
            sys.stderr.write('WARNING: Previous declaration of %s in transform %s. Overwriting...' % (n, module))
        else:
            print ('Installing transform %s from %s...' % (n, module))
            transforms[n] = module

        intype = spec.inputs[i][1]._type_

        sets = None
        if spec.inputs[i][0] is not None:
            setdir = os.path.join(setsdir, spec.inputs[i][0])
            if not os.path.exists(setdir):
                os.mkdir(setdir)
            open(os.path.join(setdir, n), 'w').close()
            sets=Set(spec.inputs[i][0])

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


        ElementTree(transform).write(os.path.join(installdir, '%s.transform' % n))

        transformsettings = TransformSettings(properties=[
            CmdLineTransformPropertySetting(
                os.path.join(get_bin_dir(),
                'dispatcher.bat' if os.name == 'nt' else 'dispatcher')
            ),
            CmdParmTransformPropertySetting(name),
            CmdCwdTransformPropertySetting(working_dir),
            CmdDbgTransformPropertySetting(spec.debug)
        ])
        ElementTree(transformsettings).write(os.path.join(installdir, '%s.transformsettings' % n))


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


def installmtz(package, prefix):
    try:
        src = resource_filename('%s.resources.maltego' % package, 'entities.mtz')
        if not os.path.exists(src):
            return
        prefix = os.path.join(prefix, 'config', 'Maltego', 'Entities')
        z = ZipFile(src)
        entities = filter(lambda x: x.endswith('.entity'), z.namelist())

        for e in entities:
            data = z.open(e).read()
            xml = XML(data)
            category = xml.get('category')
            catdir = os.path.join(prefix, category)
            if not os.path.exists(catdir):
                os.mkdir(catdir)
            p = os.path.join(catdir, os.path.basename(e))
            print 'Installing entity %s to %s...' % (e, p)
            with open(p, 'wb') as f:
                f.write(data)
    except ImportError:
        pass


def installnbattr(xml, src, dst):
    src = findall('machine\(([^\)]+)', src)[0]
    if not src:
        return
    props = sub('\s*\n\s*|"', '', src).split(',')
    e = None
    for p in props:
        if ':' not in p:
            if xml.find('fileobject[@name="%s"]' % dst) is not None:
                return
            e = SubElement(xml, 'fileobject')
            e.set('name', dst)
        else:
            n, v = p.split(':')
            s = SubElement(e, 'attr')
            s.set('name', n)
            s.set('stringvalue', v)
    s = SubElement(e, 'attr')
    s.set('name', 'readonly')
    s.set('boolvalue', 'false')
    s = SubElement(e, 'attr')
    s.set('name', 'enabled')
    s.set('boolvalue', 'true')


def installmachines(package, prefix):
    try:
        prefix = os.path.join(prefix, 'config', 'Maltego', 'Machines')
        n = os.path.join(prefix, '.nbattrs')
        e = XML('<attributes version="1.0"/>')
        if os.path.exists(n):
            e = XML(file(n).read())
        if not os.path.exists(prefix):
            os.mkdir(prefix)
        package = '%s.resources.maltego' % package
        for m in filter(lambda x: x.endswith('.machine'), resource_listdir(package, '')):
            src = resource_filename(package, m)
            dst = os.path.join(prefix, m)
            print 'Installing machine %s to %s...' % (src, dst)
            with open(dst, 'wb') as f:
                data = file(src).read()
                f.write(data)
                installnbattr(e, data, m)
        ElementTree(e).write(file(n, 'wb'))
    except ImportError, e:
        pass



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
        print ("Does not appear to be a valid canari package. "
               "Couldn't import the '%s.transforms' package in '%s'. Error message: %s" % (opts.package, opts.package, e))
        exit(-1)

    for t in m.__all__:
        transform = '%s.transforms.%s' % (opts.package, t)

        m2 = import_transform(transform)
        if hasattr(m2, 'dotransform') and hasattr(m2.dotransform, 'label'):
            install_transform(
                m2.__name__,
                transform,
                getattr(m2, '__author__', ''),
                m2.dotransform,
                opts.settings_dir,
                opts.working_dir
            )

    installmtz(opts.package, opts.settings_dir)
    installmachines(opts.package, opts.settings_dir)

    if not transforms:
        print ('Error: no transforms found...')
        exit(-1)
