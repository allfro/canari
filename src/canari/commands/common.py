#!/usr/bin/env python

from distutils.command.install import install
from distutils.dist import Distribution
from setuptools import find_packages
from pkgutil import iter_modules
from argparse import Action
from datetime import datetime
from string import Template
import unicodedata
import subprocess
import sys
import os
import re

from pkg_resources import resource_filename

from canari.commands.framework import Command
from canari.config import CanariConfigParser
from canari.utils.console import highlight

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = ['Andrew Udvare']

__license__ = 'GPL'
__version__ = '0.6'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class ParseFieldsAction(Action):
    """
    Custom argparse action to parse arguments for the run- and debug-transform commands. This ensures that all
    positional arguments are parsed and stored correctly.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        # Does the value argument have an equals ('=') sign that is not escaped and is the params argument populated?
        if namespace.params and re.search(r'(?<=[^\\])=', namespace.value):
            # if so, apply fix and pop last element of namespace.params into namespace.value
            # and copy what was in namespace.value into namespace.fields to fix everything
            values = namespace.value
            namespace.value = namespace.params.pop().replace('\=', '=')
            namespace.fields = values
            # Next parse our fields argument into a dictionary
            fs = re.split(r'(?<=[^\\])#', values)
            if fs:
                namespace.fields = dict(
                    map(
                        lambda x: [
                            c.replace('\#', '#').replace('\=', '=').replace('\\\\', '\\')
                            for c in re.split(r'(?<=[^\\])=', x, 1)
                        ],
                        fs
                    )
                )


@Command(description='Centralized Canari Management System')
def canari_main(opts):
    """
    This is the main function for the Canari commander. Nothing special here.
    """
    fix_pypath()
    opts.command_function(opts)


def get_bin_dir():
    """
    Returns the absolute path of the installation directory for the Canari scripts.
    """
    d = install(Distribution())
    d.finalize_options()
    return d.install_scripts


def to_utf8(s):
    return unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore')


def sudo(args):
    p = subprocess.Popen([os.path.join(get_bin_dir(), 'pysudo')] + args, stdin=subprocess.PIPE)
    p.communicate()
    return p.returncode


def uproot():
    if os.name == 'posix' and not os.geteuid():
        login = os.getlogin()

        if login != 'root':
            print 'Why are you using root to run this command? You should be using %s! Bringing you down...' % login
            import pwd

            user = pwd.getpwnam(login)
            os.setgid(user.pw_gid)
            os.setuid(user.pw_uid)


def read_template(name, values):
    t = Template(file(resource_filename('canari.resources.template', '%s.plate' % name)).read())
    return t.substitute(**values)


def write_template(dst, data):
    print('creating file %s...' % dst)
    with file(dst, mode='wb') as w:
        w.write(data)


def generate_all(*args):
    return "\n\n__all__ = [\n    '%s'\n]" % "',\n    '".join(args)


def build_skeleton(*args):
    for d in args:
        if isinstance(d, list):
            d = os.sep.join(d)
        print('creating directory %s' % d)
        os.mkdir(d)


def fix_pypath():
    if '' not in sys.path:
        sys.path.insert(0, '')


def fix_binpath(paths):
    if paths is not None and paths:
        if isinstance(paths, basestring):
            os.environ['PATH'] = paths
        elif isinstance(paths, list):
            os.environ['PATH'] = os.pathsep.join(paths)


def import_transform(script):
    return __import__(script, globals(), locals(), ['dotransform'])


def import_package(package):
    return __import__(package, globals(), locals(), ['*'])


def init_pkg():
    root = project_root()

    if root is not None:
        conf = os.path.join(root, '.canari')
        if os.path.exists(conf):
            c = CanariConfigParser()
            c.read(conf)
            return {
                'author': c['metadata/author'],
                'email': c['metadata/email'],
                'maintainer': c['metadata/maintainer'],
                'project': c['metadata/project'],
                'year': datetime.now().year
            }

    return {
        'author': '',
        'email': '',
        'maintainer': '',
        'project': '',
        'year': datetime.now().year
    }


def project_root():
    marker = '.canari'
    for i in range(0, 5):
        if os.path.exists(marker) and os.path.isfile(marker):
            return os.path.dirname(os.path.realpath(marker))
        marker = '..%s%s' % (os.sep, marker)
    raise ValueError('Unable to determine project root.')


def project_tree(package=None):
    """Returns a dict of the project tree.

    Will try and look for local/source packages first, and if it fails to find
    a valid project root, it will look for system installed packages instead.

    Returns a dictionary with the following fields:
    - root: Path of the canari root folder or None if not applicable.
    - src: Path of the folder containing the package.
    - pkg: Path of the actual package.
    - pkg_name: Name of the package, which details are returned about.
    - resources: Path of the resources folder inside the package.
    - transforms: Path of the transforms folder inside the package.
    """

    # Default values for the returned fields.
    tree = dict(
        root=None,
        src=None,
        pkg=None,
        pkg_name=None,
        resources=None,
        transforms=None,
    )


    try:
        root = project_root()

        # TODO: The 'src' folder is currently harcoded inside setup.py. People
        # may change this and thus we should probably read this value from
        # '.canari', so the user may change this freely.

        # Using find_packages we don't risk having to deal with the *.egg-info
        # folder and trying to make a best guess at what folder is a actual
        # source code, tests, or something else.
        packages = filter(lambda pkg: pkg.find('.') < 0, find_packages('src'))
        if package is None and len(packages) == 1:
            # No package was specified by the user and there is only one
            # possibility, so silently choose that one.
            package = packages[0]
        elif package not in packages:
            # The supplied package was not found or not specified (None).  List
            # the found packages and make the user choose the correct one.
            if package is not None:
                print "{warning} You specified a specific transform package, but " \
                    "it does {_not_} exist inside this canari source directory. " \
                    "\nPerhaps you ment to refer to an already installed package?\n" \
                        .format(warning = highlight('[warning]', 'red', False),
                                _not_= highlight('not', None, True))

            print "The possible transform packages inside this canari root directory are:"
            print 'Root dir: %s' % root
            n = parse_int('Choose a package', packages, default=0)
            package = packages[n]

        #else: the user supplied package name is already a valid one, and the
        #one the user picked.. so all is good.
        assert package is not None, 'Fatal error: No package has been found or choosen!'

        # Update the tree dict with all relevant information for this source package
        tree['root'] = root
        # Again 'src' is hardcooded in setup.py
        tree['src'] = os.path.join(tree['root'], 'src')
        tree['pkg'] = os.path.join(tree['src'], package)
    except ValueError as ve:
        # If we can't locate the project root, then we are not within a (source)
        # canari project folder and thus we will try and look for installed
        # packages instead.
        for module_importer, name, ispkg in iter_modules():
            # module_importer is most likely a pkgutils.ImpImporter instance (or
            # the like) that has been initialised with a path that matches the
            # (egg) install directory of the current module being iterated.
            # Thus any calls to functions (e.g., find_module) on this instance
            # will be limited to that path (i.e., you can't load arbitrary
            # packages from it).
            if name == package:
                # Installed packages, don't have a (canari) 'root' folder.
                # However it seems that (atleast) installed eggs have a form of
                # 'src' folder named #pkg_name#-#pkg_version#-#py_version#.egg.
                # This folder (generally) contains two folders: #pkg_name# and
                # EGG-INFO
                tree['src'] = module_importer.path
                tree['pkg'] = module_importer.find_module(package).filename

                break # No need to keep searching.

        if tree['src'] is None:
            # We didn't find the user supplied package name in the list of
            # installed packages.
            raise ValueError("You are not inside a canari root directory ('%s'), "
                             "and it was not possible to locate " "the given package "
                             "'%s' among the list of installed packages."
                             % (os.getcwd(), package))


    tree['pkg_name'] = package
    # A transform packages structure is expected to have a 'pkg_name.resources'
    # and 'pkg_name.transforms', thus we won't dynamically look for these as
    # everything else will break, if they can't be imported as such.

    # TODO: Here be dragons. Does python3 module madness break this assumption
    # with its new fancy features of ways to have modules not nessesarily
    # stricly tied to the file system?
    tree['resources'] = os.path.join(tree['pkg'], 'resources')
    tree['transforms'] = os.path.join(tree['pkg'], 'transforms')
    return tree


def parse_bool(question, default=True):
    choices = 'Y/n' if default else 'y/N'
    default = 'Y' if default else 'N'
    while True:
        ans = raw_input('%s [%s]: ' % (question, choices)).upper() or default
        if ans.startswith('Y'):
            return True
        elif ans.startswith('N'):
            return False
        else:
            print('Invalid selection (%s) must be either [y]es or [n]o.' % ans)


def parse_int(question, choices, default=0):
    while True:
        for i, c in enumerate(choices):
            print('[%d] - %s' % (i, c))
        ans = raw_input('%s [%d]: ' % (question, default)) or default
        try:
            ans = int(ans)
            if not 0 <= ans <= i:
                raise ValueError
            return ans
        except ValueError:
            print('Invalid selection (%s) must be an integer between 0 and %d.' % (ans, i))


def parse_str(question, default):
    return raw_input('%s [%s]: ' % (question, default)) or default


class pushd(object):
    """
    Ripped from here: https://gist.github.com/Tatsh/7131812
    """

    def __init__(self, dir_name):
        self.cwd = os.path.realpath(dir_name)
        self.original_dir = None

    def __enter__(self):
        self.original_dir = os.getcwd()
        os.chdir(self.cwd)
        return self

    def __exit__(self, type_, value, tb):
        os.chdir(self.original_dir)
