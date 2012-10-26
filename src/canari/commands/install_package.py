#!/usr/bin/env python

from ..maltego.configuration import  (MaltegoTransform, CmdCwdTransformProperty, CmdDbgTransformProperty,
                               CmdLineTransformProperty, CmdParmTransformProperty, InputConstraint, TransformSet,
                               TransformSettings, CmdCwdTransformPropertySetting, CmdDbgTransformPropertySetting,
                               CmdLineTransformPropertySetting, CmdParmTransformPropertySetting)
from common import detect_settings_dir, cmd_name, fix_pypath, get_bin_dir
from ..maltego.message import  ElementTree

from os import sep, path, mkdir, chdir, getcwd, name
from pkg_resources import resource_filename
from argparse import ArgumentParser
from string import Template
from sys import stderr
from re import sub



__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
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
    default=getcwd(),
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
def help():
    parser.print_help()


def description():
    return parser.description


# Extra sauce to parse args
def parse_args(args):
    args = parser.parse_args(args)

    if args.settings_dir is detect_settings_dir:
        args.settings_dir = detect_settings_dir()

    return args


# Logic to install transforms
def install_transform(module, name, author, spec, prefix, working_dir):

    installdir = sep.join([prefix, 'config', 'Maltego', 'TransformRepositories', 'Local'])

    if not path.exists(installdir):
        mkdir(installdir)

    setsdir = sep.join([prefix, 'config', 'Maltego', 'TransformSets'])

    for i,n in enumerate(spec.uuids):

        if n in transforms:
            stderr.write('WARNING: Previous declaration of %s in transform %s. Overwriting...' % (n, module))
        else:
            print ('Installing transform %s from %s...' % (n, module))
            transforms[n] = module

        intype = spec.inputs[i][1]('').type

        sets = None
        if spec.inputs[i][0] is not None:
            setdir = sep.join([setsdir, spec.inputs[i][0]])
            if not path.exists(setdir):
                mkdir(setdir)
            open(sep.join([setdir, n]), 'w').close()
            sets=TransformSet(spec.inputs[i][0])

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


        ElementTree(transform).write(sep.join([installdir, '%s.transform' % n]))

        transformsettings = TransformSettings(properties=[
            CmdLineTransformPropertySetting(path.join(get_bin_dir(), 'dispatcher')),
            CmdParmTransformPropertySetting(name),
            CmdCwdTransformPropertySetting(working_dir),
            CmdDbgTransformPropertySetting(spec.debug)
        ])
        ElementTree(transformsettings).write(sep.join([installdir, '%s.transformsettings' % n]))


def writeconf(sf, df, **kwargs):
    if not path.exists(df):
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
    ld = getcwd()
    chdir(path.dirname(f))

    import canari.config as config
    reload(config)

    if c not in config.config['default/configs']:
        print ('Updating %s...' % f)
        s = ''
        with file(f) as r:
            s = r.read()
        with file(f, mode='wb') as w:
            w.write(sub(r'configs\s*\=', 'configs = %s,' % c, s))
    chdir(ld)


def installconf(opts, args):
    src = resource_filename('canari.resources.template', 'canari.plate')
    writeconf(
        src,
        sep.join([opts.working_dir, 'canari.conf']),
        sub=True,
        command=' '.join(['canari install'] + args),
        config=('%s.conf' % opts.package) if opts.package != 'canari' else '',
        path='${PATH},/usr/local/bin,/opt/local/bin' if name == 'posix' else ''
    )

    if opts.package != 'canari':
        src = resource_filename('%s.resources.etc' % opts.package, '%s.conf' % opts.package)
        writeconf(src, sep.join([opts.working_dir, '%s.conf' % opts.package]), sub=False)
        updateconf('%s.conf' % opts.package, sep.join([opts.working_dir, 'canari.conf']))

# Main
def run(args):

    opts = parse_args(args)

    fix_pypath()


    if opts.package.endswith('.transforms'):
        opts.package = opts.package.replace('.transforms', '')

    try:
        installconf(opts, args)
    except ImportError:
        pass

    print ('Looking for transforms in %s.transforms' % opts.package)
    try:
        m = __import__('%s.transforms' % opts.package, globals(), locals(), ['*'])
    except ImportError:
        print "Not a valid canari package. Couldn't find the '%s.transforms' package in '%s'." % (opts.package, opts.package)
        exit(-1)

    for t in m.__all__:
        transform = '%s.transforms.%s' % (opts.package, t)

        m2 = __import__(transform, globals(), locals(), ['dotransform'])
        if hasattr(m2, 'dotransform') and hasattr(m2.dotransform, 'label'):
            install_transform(
                m2.__name__,
                transform,
                getattr(m2, '__author__', ''),
                m2.dotransform,
                opts.settings_dir,
                opts.working_dir
            )

    if not transforms:
        print ('Error: no transforms found...')
        exit(-1)
